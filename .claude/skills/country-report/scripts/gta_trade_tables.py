"""
GTA trade tables for a country economic report.

Deterministic, reused for BOTH exports and imports and for BOTH the HS2 and the
partner-country breakdowns — so it lives here once instead of being re-derived
on every report.

For a reporter country it produces, per direction (Export/Import) and per
grouping (HS2 chapter / partner country):

  * top-10 table for the latest available year      -> *_top10_*.csv
  * contribution-to-growth, top-5 + "Others", by year (for the stacked bar)
                                                     -> *_contrib_*.csv
  * contribution-to-growth, FULL sorted list, latest year (for the appendix)
                                                     -> *_contrib_*_full.csv

Contribution of group i to total %YoY growth in year t:
    contrib_i,t = (V_i,t - V_i,t-1) / V_total,t-1 * 100
(The segments in a year sum to the total %YoY growth of the aggregate.)

Note: GTA uses **2-letter** ISO codes (Reporter_ISO/Partner_ISO/meta_iso.ISO),
e.g. Indonesia = 'ID', Vietnam = 'VN', Thailand = 'TH'.

Usage
-----
  & '.\\bin\\python.ps1' '.claude/skills/country-report/scripts/gta_trade_tables.py' \
        --gta-code ID --outdir output/data/country_report/Indonesia --years 5
"""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd


def find_project_root() -> Path:
    """Walk up from this file until a folder containing `database/` is found."""
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / "database").is_dir():
            return p
    return Path.cwd()


def locate_gta_db(root: Path) -> Path:
    for cand in (root / "database" / "GTA.db", root / "database" / "core" / "GTA.db"):
        if cand.exists():
            return cand
    raise FileNotFoundError("GTA.db not found under database/ or database/core/")


def load_annual(con: sqlite3.Connection, iso3: str, direction: str, group_col: str) -> pd.DataFrame:
    """Return annual totals: columns [Year, key, label, USD]."""
    if group_col == "HS2_Code":
        sql = """
            SELECT g.Year AS Year,
                   g.HS2_Code AS key,
                   COALESCE(m.HS2_Desc_EN, printf('%02d', g.HS2_Code)) AS label,
                   SUM(g.USD) AS USD
            FROM GTA g
            LEFT JOIN meta_hs2 m ON g.HS2_Code = m.HS2_Code
            WHERE g.Reporter_ISO = ? AND g.Trade_Direction = ?
            GROUP BY g.Year, g.HS2_Code
        """
    else:  # Partner_ISO
        sql = """
            SELECT g.Year AS Year,
                   g.Partner_ISO AS key,
                   COALESCE(m.Name_EN, g.Partner_ISO) AS label,
                   SUM(g.USD) AS USD
            FROM GTA g
            LEFT JOIN meta_iso m ON g.Partner_ISO = m.ISO
            WHERE g.Reporter_ISO = ? AND g.Trade_Direction = ?
            GROUP BY g.Year, g.Partner_ISO
        """
    df = pd.read_sql_query(sql, con, params=(iso3, direction))
    return df


def short_label(label: str, width: int = 32) -> str:
    """Concise legend label for long HS2 descriptions (partner names pass through)."""
    s = str(label).strip()
    return s if len(s) <= width else s[: width - 1].rstrip() + "…"


def report_year_for(con: sqlite3.Connection, reporter: str) -> int:
    """Latest year with a full 12 months of data for this reporter; otherwise the
    latest year present. Avoids treating a partial current year as 'last year'."""
    rows = con.execute(
        "SELECT Year, COUNT(DISTINCT Month) FROM GTA "
        "WHERE Reporter_ISO = ? GROUP BY Year ORDER BY Year",
        (reporter,),
    ).fetchall()
    complete = [y for (y, nmonths) in rows if nmonths >= 12]
    if complete:
        return int(max(complete))
    return int(max(y for (y, _) in rows))


def build_top10(df: pd.DataFrame, year: int) -> pd.DataFrame:
    cur = df[df["Year"] == year].copy()
    total = cur["USD"].sum()
    cur["Share_pct"] = cur["USD"] / total * 100 if total else 0
    cur = cur.sort_values("USD", ascending=False).head(10)
    cur["USD_bn"] = cur["USD"] / 1e9
    return cur[["label", "USD_bn", "Share_pct"]].reset_index(drop=True)


def build_contribution(df: pd.DataFrame, years: int, end_year: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (tidy_top5_plus_others, full_latest_year_sorted), ending at end_year."""
    all_years = [y for y in sorted(df["Year"].unique()) if y <= end_year]
    keep_years = all_years[-(years + 1):]  # need one extra year for the first YoY
    wide = (
        df[df["Year"].isin(keep_years)]
        .pivot_table(index="label", columns="Year", values="USD", aggfunc="sum")
        .fillna(0.0)
    )

    # contribution_i,t = (V_t - V_{t-1}) / total_{t-1} * 100
    contrib = {}
    for i in range(1, len(keep_years)):
        t, tm1 = keep_years[i], keep_years[i - 1]
        total_prev = wide[tm1].sum()
        contrib[t] = (wide[t] - wide[tm1]) / total_prev * 100 if total_prev else wide[t] * 0
    contrib = pd.DataFrame(contrib)  # index=label, columns=year

    latest = contrib.columns.max()
    ranking = contrib[latest].abs().sort_values(ascending=False)
    top5 = list(ranking.head(5).index)

    # tidy top5 + Others, across years
    tidy_rows = []
    for yr in contrib.columns:
        others = 0.0
        for label, val in contrib[yr].items():
            if label in top5:
                tidy_rows.append({
                    "Year": int(yr),
                    "Group": short_label(label),
                    "Group_full": label,
                    "Contribution_pct": round(val, 4),
                })
            else:
                others += val
        tidy_rows.append({"Year": int(yr), "Group": "Others", "Group_full": "Others",
                          "Contribution_pct": round(others, 4)})
    tidy = pd.DataFrame(tidy_rows)

    # full sorted list for the latest year (appendix)
    full = (
        contrib[latest]
        .sort_values(ascending=False)
        .rename("Contribution_pct")
        .reset_index()
        .rename(columns={"label": "Group"})
    )
    full["Year"] = int(latest)
    full["Contribution_pct"] = full["Contribution_pct"].round(4)
    return tidy, full[["Year", "Group", "Contribution_pct"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gta-code", dest="gta_code", required=True,
                    help="Reporter 2-letter GTA ISO code, e.g. ID (Indonesia), VN, TH")
    ap.add_argument("--outdir", required=True, help="Output data dir for this country report")
    ap.add_argument("--years", type=int, default=5, help="Years of contribution history")
    args = ap.parse_args()

    root = find_project_root()
    db = locate_gta_db(root)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    written = []
    with sqlite3.connect(db) as con:
        # sanity: does this reporter exist?
        n = con.execute(
            "SELECT COUNT(*) FROM GTA WHERE Reporter_ISO = ?", (args.gta_code,)
        ).fetchone()[0]
        if n == 0:
            print(f"[WARN] No GTA rows for Reporter_ISO='{args.gta_code}'. "
                  f"Check the 2-letter GTA code or GTA coverage. Skipping trade tables.")
            return

        year = report_year_for(con, args.gta_code)

        for direction, dtag in (("Export", "exports"), ("Import", "imports")):
            for group_col, gtag in (("HS2_Code", "hs2"), ("Partner_ISO", "partner")):
                df = load_annual(con, args.gta_code, direction, group_col)
                if df.empty:
                    print(f"[WARN] No {direction} / {gtag} data for {args.gta_code}.")
                    continue

                top10 = build_top10(df, year)
                p = outdir / f"{dtag}_top10_{gtag}.csv"
                top10.to_csv(p, index=False)
                written.append(p)

                tidy, full = build_contribution(df, args.years, year)
                p = outdir / f"{dtag}_contrib_{gtag}.csv"
                tidy.to_csv(p, index=False)
                written.append(p)
                p = outdir / f"{dtag}_contrib_{gtag}_full.csv"
                full.to_csv(p, index=False)
                written.append(p)

        print(f"Latest trade year used: {year}")
    print(f"Wrote {len(written)} files to {outdir}:")
    for p in written:
        print(f"  - {p.name}")


if __name__ == "__main__":
    main()
