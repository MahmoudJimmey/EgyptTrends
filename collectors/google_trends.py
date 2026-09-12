"""
Pulls what's ALREADY trending on Google in Egypt right now.
No keywords required — this is Google's own "Trending Now" feed, read
via its public RSS feed (fast, no rate-limit issues, no browser needed).

Uses trendspyg — pytrends was archived by its maintainer in April 2025
and now fails almost immediately due to stale session handling, so it's
not usable anymore. trendspyg is the actively-maintained replacement.
"""
import json
from datetime import datetime, timezone
from trendspyg import download_google_trends_rss


def collect():
    results = []

    try:
        trends = download_google_trends_rss(geo="EG")
        for t in trends:
            results.append({
                "source": "google_trends_rss",
                "term": t.get("trend"),
                "traffic": t.get("traffic"),
            })
    except Exception as e:
        print(f"[google_trends] RSS fetch failed: {e}")

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
