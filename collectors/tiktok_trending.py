"""
Pulls trending hashtags for Egypt from TikTok Creative Center.
TikTok has no official public "trending" API, so this hits the same
backend endpoint the Creative Center website itself uses. It's unofficial —
it can break if TikTok changes their frontend. No keywords needed, this
returns whatever IS trending for the region right now.

If this breaks: fall back to manually checking
https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en
(set region = Egypt) once a day — takes 2 minutes.
"""
import json
from datetime import datetime, timezone
import requests

URL = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"


def collect():
    items = []
    params = {
        "page": 1,
        "limit": 20,
        "period": 7,
        "country_code": "EG",
        "sort_by": "popular",
    }
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(URL, params=params, headers=headers, timeout=20)
        resp.raise_for_status()
        payload = resp.json()
        for h in payload.get("data", {}).get("list", []):
            items.append({
                "source": "tiktok_trending_hashtags_eg",
                "hashtag": h.get("hashtag_name"),
                "posts": h.get("video_views") or h.get("publish_cnt"),
                "rank": h.get("rank"),
            })
    except Exception as e:
        print(f"[tiktok] trending hashtag fetch failed (expected to be fragile): {e}")

    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "platform": "tiktok",
        "items": items,
    }


if __name__ == "__main__":
    data = collect()
    with open("data/tiktok_trending.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data['items'])} TikTok trending items")
