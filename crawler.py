import os
import requests
import pandas as pd
import sqlite3
import urllib3
from requests.exceptions import SSLError
from typing import Any, Dict, List

# -----------------------------------------
# 1. CWA Weather URL (fixed: no spaces)
# -----------------------------------------
URL = ("https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001"
       "?Authorization=CWA-1FFDDAEC-161F-46A3-BE71-93C32C52829F"
       "&downloadType=WEB&format=JSON")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_data(url: str) -> Dict[str, Any]:
    """Fetch JSON data from URL.

    For minimal friction in development environments, if SSL verification fails
    the function will retry once with `verify=False`. This makes the script
    runnable without extra env vars. Be aware this bypasses certificate checks
    and should not be used in production.
    """
    try:
        resp = requests.get(url, timeout=30, verify=True)
        resp.raise_for_status()
        return resp.json()
    except SSLError:
        # Fallback for environments with problematic cert bundles
        print("SSL verification failed — retrying request with verify=False (development mode)")
        resp = requests.get(url, timeout=30, verify=False)
        resp.raise_for_status()
        return resp.json()


def parse_locations(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract location rows from JSON payload. Returns list of row dicts.

    Raises on unexpected structure.
    """
    try:
        locations = data["cwaopendata"]["resources"]["resource"]["data"]["agrWeatherForecasts"]["weatherForecasts"]["location"]
    except Exception:
        print("Unexpected JSON structure. Dumping top-level keys for inspection:")
        try:
            print(list(data.keys()))
        except Exception:
            print(repr(data)[:1000])
        raise

    rows: List[Dict[str, Any]] = []
    for loc in locations:
        name = loc["locationName"]
        maxT_list = loc["weatherElements"]["MaxT"]["daily"]
        minT_list = loc["weatherElements"]["MinT"]["daily"]

        for mx, mn in zip(maxT_list, minT_list):
            rows.append({
                "location": name,
                "date": mx["dataDate"],
                "max_temp": mx["temperature"],
                "min_temp": mn["temperature"],
            })
    return rows



def persist_rows(rows: List[Dict[str, Any]], db_path: str = "sqlightdata.db") -> None:
    df = pd.DataFrame(rows)
    print(df)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS temperature (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT,
        date TEXT,
        max_temp REAL,
        min_temp REAL
    )
    """
    )

    df.to_sql("temperature", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

    print(f"\nData successfully saved to SQLite: {db_path}")


def main() -> None:
    data = fetch_data(URL)
    rows = parse_locations(data)
    persist_rows(rows)


if __name__ == "__main__":
    main()
