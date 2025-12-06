import sqlite3
from pathlib import Path
import pandas as pd

import streamlit as st


DB_PATH = Path("sqlightdata.db")


# Cache the loaded data, but include the DB file mtime in the cache key so
# the cache is invalidated automatically when the DB file changes.
@st.cache_data
def load_data(db_path: Path, db_mtime: float) -> pd.DataFrame:
    if not db_path.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(str(db_path))
    try:
        df = pd.read_sql_query("SELECT location, date, max_temp, min_temp FROM temperature", conn)
    finally:
        conn.close()
    # Ensure correct dtypes
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def main() -> None:
    st.set_page_config(page_title="Crawler Temperatures", layout="wide")
    st.title("Weather Forecasts — Location Viewer")

    db_mtime = DB_PATH.stat().st_mtime if DB_PATH.exists() else 0
    df = load_data(DB_PATH, db_mtime)
    if st.button("Refresh data"):
        # Force Streamlit to rerun the script (immediate refresh)
        st.experimental_rerun()
    if df.empty:
        st.warning(f"Database not found or no data in `{DB_PATH}`. Run crawler to populate data.")
        return

    locations = sorted(df["location"].unique().tolist())
    locations.insert(0, "All Locations")

    selected = st.selectbox("Select location", locations)

    if selected == "All Locations":
        view = df.copy()
    else:
        view = df[df["location"] == selected].copy()

    st.subheader(f"Showing: {selected}")
    st.dataframe(view.sort_values(["location", "date"]).reset_index(drop=True))

    if not view.empty:
        # pivot by date
        chart_df = view.groupby("date").agg({"max_temp": "mean", "min_temp": "mean"}).reset_index()
        chart_df = chart_df.sort_values("date")
        chart_df = chart_df.set_index("date")
        st.line_chart(chart_df)


if __name__ == "__main__":
    main()
