"""
Pulls YouTube's official "Trending" chart for Egypt (regionCode=EG).
Uses the free YouTube Data API v3 — no keywords needed, this is Google's
own trending chart for the region.

Requires: a YOUTUBE_API_KEY (free from Google Cloud Console, YouTube Data API v3 enabled).
"""
import json
import os
from datetime import datetime, timezone
import requests

API_KEY = os.environ.get("YOUTUBE_API_KEY")
URL = "https://www.googleapis.com/youtube/v3/videos"


def collect():
    if not API_KEY:
        print("[youtube] YOUTUBE_API_KEY not set, skipping")
        return {"collected_at": datetime.now(timezone.utc).isoformat(),
                "platform": "youtube", "items": []}

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": "EG",
        "maxResults": 25,
        "key": API_KEY,
    }
    resp = requests.get(URL, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for v in data.get("items", []):
        snippet = v.get("snippet", {})
        stats = v.get("statistics", {})
        items.append({
            "source": "youtube_trending_eg",
            "title": snippet.get("title"),
            "channel": snippet.get("channelTitle"),
            "category_id": snippet.get("categoryId"),
            "views": stats.get("viewCount"),
            "likes": stats.get("likeCount"),
            "comments": stats.get("commentCount"),
            "published_at": snippet.get("publishedAt"),
            "url": f"https://www.youtube.com/watch?v={v.get('id')}",
        })

    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "platform": "youtube",
        "items": items,
    }


if __name__ == "__main__":
    data = collect()
    with open("data/youtube_trending.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data['items'])} YouTube trending items")
