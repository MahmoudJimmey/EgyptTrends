"""
Pulls what's ALREADY trending on Google in Egypt right now.
No keywords required — this is Google's own "Trending Now" feed.
"""
import json
from datetime import datetime, timezone
from pytrends.request import TrendReq


def collect():
    pytrends = TrendReq(hl="en-US", tz=120)  # tz=120 -> Egypt (UTC+2), adjust for DST if needed
    results = []

    try:
        # Daily trending searches for Egypt
        df = pytrends.trending_searches(pn="egypt")
        for term in df[0].tolist():
            results.append({"source": "google_trends_daily", "term": term})
    except Exception as e:
        print(f"[google_trends] daily trending failed: {e}")

    try:
        # Realtime trending searches (more up to the minute, when available for the region)
        rt = pytrends.realtime_trending_searches(pn="EG")
        for _, row in rt.iterrows():
            results.append({
                "source": "google_trends_realtime",
                "term": row.get("title", ""),
                "related": row.get("entityNames", []),
            })
    except Exception as e:
        print(f"[google_trends] realtime trending failed: {e}")

    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "platform": "google_trends",
        "items": results,
    }


if __name__ == "__main__":
    data = collect()
    with open("data/google_trends.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data['items'])} Google Trends items")
