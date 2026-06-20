"""
Deflator Prediction Pipeline - Step 1: Data Preparation.

Fetches Thailand's GDP Deflator (CEIC series 367523747, quarterly index),
caches it to the pipeline DB, and assembles a single wide quarterly frame
combining the target with three already-forecasted exogenous price indices.

To maximise the historical estimation window, the Headline CPI exogenous is
built by splicing the LONG-HISTORY actual headline CPI (CEIC 541395757, back to
1976) over the historical period with the prepared-food *shock* CPI forecast
chained on (by quarter-on-quarter growth) over the forecast window. The actual
and reconstructed-shock CPI are ~99.95% correlated over their overlap, so the
splice is continuous. This anchors the level to official data while preserving
the requested shock scenario's forward dynamics.

  - Headline_CPI       (actual 541395757 history + shock-growth forecast)
  - bot_export_price_index  (already quarterly, 2000-Q1 onward)
  - bot_import_price_index  (already quarterly, 2000-Q1 onward)

Output: output/data/deflator_prediction/deflator_prediction_input_quarterly.csv
"""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SID_DEFLATOR = "367523747"      # GDP Deflator: Thailand (quarterly index)
SID_CPI = "541395757"           # Consumer Price Index (headline, actual index level)

DB_PATH = ROOT / "database" / "deflator_prediction" / "deflator_prediction.db"
CPI_SHOCK = ROOT / "output" / "data" / "prepared_food_shock" / "prepared_food_shock_comparison.csv"
EXIM_Q = ROOT / "output" / "data" / "ex_im_price_forecast" / "export_import_price_forecast_quarterly.csv"
OUT_DIR = ROOT / "output" / "data" / "deflator_prediction"

TARGET = "gdp_deflator"
CPI_COL = "Headline_CPI"
EXOG_COLS = [CPI_COL, "bot_export_price_index", "bot_import_price_index"]


def _fetch_ceic(series_id: str, table: str) -> pd.DataFrame:
    """Fetch a CEIC series; cache to pipeline DB; fall back to cache on failure. Long df."""
    try:
        from src.api.ceic_client import CeicSession
        sess = CeicSession()
        sess.authenticate()
        df = sess.get_data(series_id, with_historical_extension=True, count=20000)
        if not df.empty:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(DB_PATH))
            cache = df.copy()
            cache["date"] = pd.to_datetime(cache["date"]).dt.strftime("%Y-%m-%d")
            cache.to_sql(table, conn, if_exists="replace", index=False)
            conn.close()
            print(f"[fetch] {series_id}: {len(df)} obs - '{df['series_name'].iloc[0]}'")
            return df
        print(f"[fetch] {series_id}: no data; falling back to cache.")
    except Exception as e:
        print(f"[fetch] {series_id}: failed ({e}); falling back to cache.")

    conn = sqlite3.connect(str(DB_PATH))
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"])
    print(f"[cache] {series_id}: loaded {len(df)} obs from DB.")
    return df


def _to_quarterly(df_long: pd.DataFrame, name: str) -> pd.Series:
    """Monthly/quarterly long df -> quarterly-period mean Series."""
    s = df_long.sort_values("date").set_index("date")["value"].resample("QE").mean()
    s.index = pd.PeriodIndex(s.index, freq="Q")
    return s.rename(name)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # --- Target: GDP deflator (quarterly index) ---
    defl_long = _fetch_ceic(SID_DEFLATOR, "deflator_raw_long")
    defl = _to_quarterly(defl_long, TARGET).to_frame()
    defl = defl[~defl.index.duplicated(keep="last")]
    last_hist_q = defl[TARGET].dropna().index.max()   # last quarter with an actual deflator

    # --- Exogenous CPI: actual long history spliced with shock-growth forecast ---
    cpi_actual = _to_quarterly(_fetch_ceic(SID_CPI, "cpi_raw_long"), CPI_COL)

    shock = pd.read_csv(CPI_SHOCK, parse_dates=["date"]).set_index("date")["Headline_CPI_shock"]
    shock_q = shock.resample("QE").mean()
    shock_q.index = pd.PeriodIndex(shock_q.index, freq="Q")

    # Forecast quarters = beyond the deflator's last historical quarter.
    fc_q = [q for q in shock_q.index if q > last_hist_q]
    cpi = cpi_actual.loc[cpi_actual.index <= last_hist_q].copy()   # history = actual
    anchor = cpi.loc[last_hist_q]
    prev = anchor
    for q in fc_q:                                                  # forecast = chained shock growth
        g = shock_q.loc[q] / shock_q.loc[q - 1]
        prev = prev * g
        cpi.loc[q] = prev
    cpi = cpi.sort_index()

    # --- Exogenous: export / import price indices (already quarterly) ---
    exim = pd.read_csv(EXIM_Q, index_col=0, parse_dates=True).sort_index()
    exim_q = exim[["bot_export_price_index", "bot_import_price_index"]]
    exim_q.index = pd.PeriodIndex(exim_q.index, freq="Q")

    # --- Merge into one wide quarterly frame ---
    merged = (
        defl.join(cpi, how="outer")
        .join(exim_q, how="outer")
        .sort_index()
    )

    # Keep only quarters where ALL exogenous are available (forecast = target NaN).
    merged = merged.loc[merged[EXOG_COLS].notna().all(axis=1)]
    merged["is_forecast"] = merged[TARGET].isna().astype(int)

    # Period index -> quarter-end timestamp for CSV output
    out = merged.copy()
    out.index = merged.index.to_timestamp(how="end").normalize()
    out.index.name = "date"

    out_path = OUT_DIR / "deflator_prediction_input_quarterly.csv"
    out.to_csv(out_path)

    hist = out[out["is_forecast"] == 0]
    fcst = out[out["is_forecast"] == 1]
    print(f"[input] history : {hist.index.min().date()} -> {hist.index.max().date()} ({len(hist)} q)")
    print(f"[input] forecast: {fcst.index.min().date()} -> {fcst.index.max().date()} ({len(fcst)} q)")
    print(f"[input] CPI exog: actual {SID_CPI} (history) + shock-growth chain (forecast)")
    print(f"[input] columns : {list(out.columns)}")
    print(f"[saved] {out_path}")
    return out_path


if __name__ == "__main__":
    main()
