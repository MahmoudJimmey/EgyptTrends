"""
Runs every collector, merges the results into data/latest.json,
and appends a snapshot to data/history.jsonl so the dashboard can
show trend movement over time (not just today's snapshot).
"""
import json
import os
from datetime import datetime, timezone

from collectors import google_trends, youtube_trending, reddit_rising, tiktok_trending
import sheets_client

os.makedirs("data", exist_ok=True)

COLLECTORS = [
    google_trends.collect,
    youtube_trending.collect,
    reddit_rising.collect,
    tiktok_trending.collect,
]


def main():
    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "platforms": [],
    }

    for collect_fn in COLLECTORS:
        try:
            result = collect_fn()
            snapshot["platforms"].append(result)
            print(f"{result['platform']}: {len(result['items'])} items")
        except Exception as e:
            print(f"Collector {collect_fn.__module__} crashed: {e}")

    with open("data/latest.json", "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    with open("data/history.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot, ensure_ascii=False) + "\n")

    print("Done. Wrote data/latest.json and appended data/history.jsonl")

    # Also push to Google Sheets, if configured (see README). This is what
    # gives you long-term, shareable storage instead of just local files.
    try:
        sheets_client.write_snapshot(snapshot)
    except Exception as e:
        print(f"[sheets] sync failed, continuing without it: {e}")


if __name__ == "__main__":
    main()
