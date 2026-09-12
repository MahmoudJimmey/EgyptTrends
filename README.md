# Egypt Trends Dashboard

Zero-input trend tracker. You never type a hashtag or keyword — it pulls
whatever is ALREADY trending in Egypt from each platform's own trending
feed, then shows it all in one dashboard.

## Sources
| Platform | What it pulls | Cost | Needs setup? |
|---|---|---|---|
| Google Trends | Daily + realtime trending searches, Egypt | Free | No — works out of the box |
| YouTube | "Trending" chart, region = EG | Free | Yes — needs a free API key |
| Reddit | "Rising" posts in r/Egypt, r/Cairo, r/arabs | Free | Yes — needs free app credentials |
| TikTok | Trending hashtags, Egypt | Free but unofficial | No key, but may break if TikTok changes their site |

## 1. Install

```bash
pip install -r requirements.txt
```

## 2. Set up free API keys (5–10 minutes, one time)

**YouTube** (optional but recommended):
1. Go to console.cloud.google.com → create a project
2. Enable "YouTube Data API v3"
3. Create an API key under Credentials
4. `export YOUTUBE_API_KEY=your_key`

**Reddit** (optional but recommended):
1. Go to reddit.com/prefs/apps → "create app" → choose "script"
2. Copy the client ID and secret
3. `export REDDIT_CLIENT_ID=your_id`
4. `export REDDIT_CLIENT_SECRET=your_secret`

Google Trends and TikTok need no keys — they'll just run.

**Google Sheets** (for storing + retrieving everything long-term):
1. Go to console.cloud.google.com → your project (or a new one)
2. Enable "Google Sheets API" and "Google Drive API"
3. Go to Credentials → Create Credentials → Service Account → create it
4. Open the service account → Keys → Add Key → JSON → download it, save as
   `service_account.json` in this project's root folder
5. Create a new Google Sheet (any name), copy the ID from its URL
   (`https://docs.google.com/spreadsheets/d/THIS_PART_IS_THE_ID/edit`)
6. Open the downloaded JSON, copy the `client_email` value, and **share
   your Google Sheet with that email** (Editor access) — this is the step
   people usually miss
7. Set:
   ```bash
   export GOOGLE_SHEETS_CREDENTIALS_FILE=service_account.json
   export SPREADSHEET_ID=your_sheet_id
   ```

Sheets is optional — if you skip this, everything still works using just
the local `data/latest.json` / `data/history.jsonl` files. Once it's set
up, every run also appends rows to your Sheet (one tab per platform), so
you get permanent, shareable, searchable storage on top of the dashboard.

## 3. Get your first snapshot

```bash
python aggregate.py
```

This writes `data/latest.json` (current snapshot) and appends to
`data/history.jsonl` (so you can track trend movement over time later).

## 4. Run the dashboard

```bash
streamlit run app.py
```

Opens in your browser. No input fields — it just shows what's trending.

## 5. Automate it (free, no server)

The included `.github/workflows/refresh.yml` runs `aggregate.py` every
6 hours on GitHub's free Actions minutes and commits the new data back
to your repo. To enable it:

1. Push this project to a GitHub repo (service_account.json is
   gitignored — never commit it)
2. Go to Settings → Secrets and variables → Actions
3. Add `YOUTUBE_API_KEY`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`,
   `SPREADSHEET_ID`, and `GOOGLE_SHEETS_CREDENTIALS_JSON` (paste the
   *entire contents* of your service_account.json as the secret value)
4. Done — it now refreshes itself and keeps writing to your Sheet

## 6. Deploy the dashboard free

Push to GitHub, then deploy at share.streamlit.io (Streamlit Community
Cloud, free tier) pointing at `app.py`. It'll pick up `data/latest.json`
from the repo, which the GitHub Action keeps updating.

## Notes

- `collectors/tiktok_trending.py` hits an undocumented endpoint TikTok's
  own Creative Center website uses. It's the only zero-keyword way to get
  TikTok trends without a paid third-party API — but it can break without
  warning. If it stops returning data, check
  ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag manually.
- Everything here reads Egypt-region signals. If you want to also compare
  against Gulf/MENA broadly (relevant for Autologist's audience), duplicate
  a collector and change the region parameter (`pn="egypt"` → another
  country code, `regionCode="EG"` → e.g. `"SA"` or `"AE"`).
