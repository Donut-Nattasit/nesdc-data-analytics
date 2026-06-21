r"""
CQM data-fetch layer.

Pulls every fetchable monthly indicator and quarterly NIPA series from CEIC (by the
numeric IDs resolved in config.py), pivots to wide format (columns = model rename),
and writes raw wide CSVs + a SQLite cache under the cqm pipeline namespace.

Manual/GIFDATA series (government investment) are NOT fetched here — they are filled
with a placeholder later in the forecasting stage.

Run:  & '.\bin\python.ps1' 'src\pipeline\cqm\fetch_data.py'
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.api.ceic_client import CeicSession
from src.pipeline.cqm.config import load_config, nipa_id_map, project_root

OUT_DATA = project_root() / "output" / "data" / "cqm"
DB_PATH = project_root() / "database" / "cqm" / "cqm_data.db"


def _fetch_wide(client: CeicSession, id_to_name: dict[str, str],
                freq: str) -> pd.DataFrame:
    """Fetch {ceic_id: rename} and return a wide DataFrame indexed by period-end date."""
    ids = list(set(id_to_name.keys()))
    print(f"  fetching {len(ids)} {freq} series from CEIC ...")
    long = client.get_data(ids, with_historical_extension=True)
    if long.empty:
        raise RuntimeError(f"No data returned for {freq} fetch")
    long["series_id"] = long["series_id"].astype(str)
    # map numeric id -> rename
    long["col"] = long["series_id"].map({str(k): v for k, v in id_to_name.items()})
    missing = sorted(set(id_to_name) - set(long["series_id"].unique()))
    if missing:
        print(f"  WARNING: {len(missing)} {freq} ids returned no data: {missing[:10]}")
    wide = (long.dropna(subset=["col"])
                .pivot_table(index="date", columns="col", values="value", aggfunc="first")
                .sort_index())
    # normalise to period-end timestamps
    if freq == "monthly":
        wide.index = pd.to_datetime(wide.index).to_period("M").to_timestamp("M")
    else:
        wide.index = pd.to_datetime(wide.index).to_period("Q").to_timestamp("Q")
    wide = wide[~wide.index.duplicated(keep="last")].sort_index()
    return wide


def fetch_all(save: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    cfg = load_config()
    client = CeicSession()

    ind_ids = {i.ceic_id: i.rename for i in cfg.indicators
               if i.ceic_id and not i.manual}
    nipa_ids = {v: k for k, v in nipa_id_map().items()}  # ceic_id -> rename

    print("Fetching monthly indicators ...")
    monthly = _fetch_wide(client, ind_ids, "monthly")
    print(f"  monthly wide: {monthly.shape}, range {monthly.index.min():%Y-%m} "
          f"-> {monthly.index.max():%Y-%m}")

    print("Fetching quarterly NIPA ...")
    nipa = _fetch_wide(client, nipa_ids, "quarterly")
    print(f"  NIPA wide: {nipa.shape}, "
          f"range {nipa.index.min():%Y}Q{nipa.index.min().quarter} "
          f"-> {nipa.index.max():%Y}Q{nipa.index.max().quarter}")

    if save:
        OUT_DATA.mkdir(parents=True, exist_ok=True)
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        monthly.to_csv(OUT_DATA / "monthly_indicators_raw.csv")
        nipa.to_csv(OUT_DATA / "nipa_quarterly_raw.csv")
        with sqlite3.connect(DB_PATH) as con:
            monthly.reset_index(names="date").to_sql(
                "monthly_indicators", con, if_exists="replace", index=False)
            nipa.reset_index(names="date").to_sql(
                "nipa_quarterly", con, if_exists="replace", index=False)
        print(f"Saved -> {OUT_DATA} and {DB_PATH}")

    return monthly, nipa


if __name__ == "__main__":
    fetch_all()
