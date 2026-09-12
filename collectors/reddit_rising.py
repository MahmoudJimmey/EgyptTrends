"""
Pulls posts that are currently RISING (Reddit's own "about to be hot" signal)
from Egypt-focused subreddits. No keywords needed — "rising" is a sort mode,
not a search.

Requires free Reddit API credentials (praw.ini or env vars):
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
"""
import json
import os
from datetime import datetime, timezone
import praw

SUBREDDITS = ["Egypt", "Cairo", "arabs"]


def collect():
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "egypt-trends-dashboard/0.1")

    if not client_id or not client_secret:
        print("[reddit] credentials not set, skipping")
        return {"collected_at": datetime.now(timezone.utc).isoformat(),
                "platform": "reddit", "items": []}

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                          user_agent=user_agent)

    items = []
    for sub in SUBREDDITS:
        try:
            for post in reddit.subreddit(sub).rising(limit=15):
                items.append({
                    "source": f"reddit_r_{sub}",
                    "title": post.title,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": f"https://reddit.com{post.permalink}",
                })
        except Exception as e:
            print(f"[reddit] r/{sub} failed: {e}")

    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "platform": "reddit",
        "items": items,
    }


if __name__ == "__main__":
    data = collect()
    with open("data/reddit_rising.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data['items'])} Reddit rising items")
