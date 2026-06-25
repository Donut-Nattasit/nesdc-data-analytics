"""
S&P Global Connect API client.

Auth: HTTP Basic — PAT as username, password as password.
Credentials: SP_USERNAME / SP_PASSWORD in .env
Database: database/SP.db
"""

import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(__file__).resolve().parents[2] / "database" / "SP.db"


class SPClient:
    """Client for the S&P Global Connect Databrowser saved-query API."""

    def __init__(self, username: str = None, password: str = None):
        self.username = username or os.getenv("SP_USERNAME")
        self.password = password or os.getenv("SP_PASSWORD")
        if not self.username or not self.password:
            raise ValueError(
                "S&P credentials not found. Set SP_USERNAME and SP_PASSWORD in .env"
            )
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

    # ------------------------------------------------------------------
    # Core fetch
    # ------------------------------------------------------------------

    def fetch(self, endpoint: str, page_size: int = 500) -> pd.DataFrame:
        """
        Fetch all records from a saved-query endpoint, handling pagination.

        Parameters
        ----------
        endpoint : str
            Full saved-query URL, e.g.
            'https://api.connect.spglobal.com/shared/v1/databrowser/savedqueries/348345/Annual'
            Query params (pageSize, pageIndex) are managed automatically.

        Returns
        -------
        pd.DataFrame — raw long-format response with Date parsed as datetime.
        """
        base = endpoint.split("?")[0]
        all_records = []
        page = 0

        while True:
            try:
                r = self.session.get(
                    base, params={"pageSize": page_size, "pageIndex": page}, timeout=60
                )
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"HTTP Error: {e}")
                break
            except requests.exceptions.ConnectionError as e:
                print(f"Connection Error: {e}")
                break
            except requests.exceptions.Timeout as e:
                print(f"Timeout Error: {e}")
                break
            except requests.exceptions.RequestException as e:
                print(f"Request Error: {e}")
                break

            batch = r.json()
            if not batch:
                break
            all_records.extend(batch)
            if len(batch) < page_size:
                break
            page += 1

        if not all_records:
            return pd.DataFrame()

        df = pd.DataFrame(all_records)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], utc=True).dt.tz_localize(None)
        return df

    # ------------------------------------------------------------------
    # Wide pivot
    # ------------------------------------------------------------------

    def fetch_wide(
        self,
        endpoint: str,
        value_col: str = "Value",
        series_col: str = "Title",
        date_col: str = "Date",
        page_size: int = 500,
    ) -> pd.DataFrame:
        """
        Fetch and pivot to wide format: rows = Date, columns = series Title.

        Returns
        -------
        pd.DataFrame — wide format, DatetimeIndex, one column per series.
        """
        df = self.fetch(endpoint, page_size=page_size)
        if df.empty:
            return df

        return (
            df.pivot_table(index=date_col, columns=series_col, values=value_col, aggfunc="first")
            .rename_axis(index=None, columns=None)
            .sort_index()
        )

    # ------------------------------------------------------------------
    # Database persistence
    # ------------------------------------------------------------------

    def save_to_db(
        self,
        endpoint: str,
        query_name: str,
        db_path: Path = None,
        page_size: int = 500,
    ) -> pd.DataFrame:
        """
        Fetch a saved query and upsert all records into SP.db.

        Creates two tables if they don't exist:
          - saved_queries  : registry of every query that has been fetched
          - series_data    : long-format observations (upsert on primary key)

        Parameters
        ----------
        endpoint : str
            Full saved-query URL.
        query_name : str
            Human-readable label stored in saved_queries (e.g. 'Thailand Manufacturing PMI').
        db_path : Path, optional
            Override default database/SP.db location.

        Returns
        -------
        pd.DataFrame — the long-format data that was saved.
        """
        db = Path(db_path) if db_path else DB_PATH
        db.parent.mkdir(parents=True, exist_ok=True)

        # Extract numeric query_id from URL if present
        match = re.search(r"/savedqueries/(\d+)", endpoint)
        query_id = int(match.group(1)) if match else None

        df = self.fetch(endpoint, page_size=page_size)
        if df.empty:
            print("No data returned — database not updated.")
            return df

        now = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(db) as con:
            cur = con.cursor()

            # --- saved_queries table ---
            cur.execute("""
                CREATE TABLE IF NOT EXISTS saved_queries (
                    query_id    INTEGER PRIMARY KEY,
                    name        TEXT NOT NULL,
                    endpoint    TEXT NOT NULL,
                    last_fetched TEXT NOT NULL
                )
            """)
            cur.execute("""
                INSERT INTO saved_queries (query_id, name, endpoint, last_fetched)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(query_id) DO UPDATE SET
                    name         = excluded.name,
                    endpoint     = excluded.endpoint,
                    last_fetched = excluded.last_fetched
            """, (query_id, query_name, endpoint.split("?")[0], now))

            # --- series_data table ---
            cur.execute("""
                CREATE TABLE IF NOT EXISTS series_data (
                    query_id         INTEGER,
                    title            TEXT,
                    date             TEXT,
                    value            REAL,
                    frequency        TEXT,
                    economic_concept TEXT,
                    country          TEXT,
                    industry         TEXT,
                    adjustment       TEXT,
                    PRIMARY KEY (query_id, title, date)
                )
            """)

            rows = [
                (
                    query_id,
                    row.get("Title"),
                    str(row.get("Date"))[:10] if pd.notna(row.get("Date")) else None,
                    row.get("Value"),
                    row.get("Frequency"),
                    row.get("EconomicConcept"),
                    row.get("SourceGeographicLocation"),
                    row.get("Industry"),
                    row.get("Adjustment"),
                )
                for row in df.to_dict("records")
            ]

            cur.executemany("""
                INSERT INTO series_data
                    (query_id, title, date, value, frequency, economic_concept,
                     country, industry, adjustment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(query_id, title, date) DO UPDATE SET
                    value            = excluded.value,
                    frequency        = excluded.frequency,
                    economic_concept = excluded.economic_concept,
                    country          = excluded.country,
                    industry         = excluded.industry,
                    adjustment       = excluded.adjustment
            """, rows)

            con.commit()

        print(f"Saved {len(df):,} rows → {db}  (query_id={query_id}, '{query_name}')")
        return df


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch S&P saved-query data")
    parser.add_argument("endpoint", help="Full saved-query URL")
    parser.add_argument("--name", default=None, help="Query name for DB registry")
    parser.add_argument("--save", action="store_true", help="Save to database/SP.db")
    parser.add_argument("--wide", action="store_true", help="Print wide-format preview")
    parser.add_argument("--out", default=None, help="CSV output path")
    args = parser.parse_args()

    client = SPClient()

    if args.save:
        name = args.name or "Unnamed Query"
        df = client.save_to_db(args.endpoint, query_name=name)
    elif args.wide:
        df = client.fetch_wide(args.endpoint)
    else:
        df = client.fetch(args.endpoint)

    print(f"Shape: {df.shape}")
    print(df.head(10).to_string())

    if args.out:
        df.to_csv(args.out)
        print(f"Saved → {args.out}")
