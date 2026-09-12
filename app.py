"""
Egypt Trends Dashboard — zero-input.
You never type a hashtag or keyword here. It just shows you what's
already trending, pulled fresh from each platform's own trending feed.

Run locally:   streamlit run app.py
"""
import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st

import sheets_client

st.set_page_config(page_title="Egypt Trends", page_icon="📈", layout="wide")

DATA_PATH = "data/latest.json"

st.title("📈 Egypt Trends Dashboard")
st.caption("What's trending right now — no keywords needed. Pulled from Google, YouTube, Reddit, and TikTok.")

source_choice = st.radio(
    "Data source",
    ["Latest snapshot (local file)", "Google Sheets (full history)"],
    horizontal=True,
)

if source_choice == "Latest snapshot (local file)":
    if not os.path.exists(DATA_PATH):
        st.warning("No data yet. Run `python aggregate.py` once to fetch the first snapshot.")
        st.stop()

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    generated_at = datetime.fromisoformat(snapshot["generated_at"])
    st.caption(f"Last refreshed: {generated_at.strftime('%Y-%m-%d %H:%M UTC')}")

    platform_tabs = st.tabs([p["platform"].replace("_", " ").title() for p in snapshot["platforms"]])

    for tab, platform_data in zip(platform_tabs, snapshot["platforms"]):
        with tab:
            items = platform_data["items"]
            if not items:
                st.info("No data collected for this platform yet — check API keys / credentials in your .env.")
                continue

            df = pd.DataFrame(items)
            st.dataframe(df, use_container_width=True, hide_index=True)

            if "source" in df.columns and len(df["source"].unique()) > 1:
                counts = df["source"].value_counts().reset_index()
                counts.columns = ["source", "count"]
                st.bar_chart(counts.set_index("source"))

else:
    st.caption("Reading everything ever collected, straight from your Google Sheet.")
    platforms = ["google_trends", "youtube", "reddit", "tiktok"]
    platform_tabs = st.tabs([p.replace("_", " ").title() for p in platforms])

    for tab, platform in zip(platform_tabs, platforms):
        with tab:
            records = sheets_client.read_platform(platform)
            if not records:
                st.info(
                    "Nothing in Google Sheets for this platform yet. Make sure "
                    "GOOGLE_SHEETS_CREDENTIALS_FILE and SPREADSHEET_ID are set, "
                    "then run `python aggregate.py`."
                )
                continue

            df = pd.DataFrame(records)
            st.dataframe(df, use_container_width=True, hide_index=True)

            if "collected_at" in df.columns:
                daily_counts = df["collected_at"].str.slice(0, 10).value_counts().sort_index()
                st.line_chart(daily_counts)

st.divider()
st.caption(
    "Tip: schedule `aggregate.py` with the included GitHub Action to refresh this "
    "automatically (e.g. every 6 hours) and deploy this app free on Streamlit Community Cloud."
)
