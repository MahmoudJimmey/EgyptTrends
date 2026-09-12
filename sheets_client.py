"""
Thin wrapper around gspread so the rest of the project doesn't need to
know anything about Google's auth flow. Google Sheets is used here as
free, shareable, persistent storage — every collector run appends its
rows to a tab named after the platform, plus a running "history" log.

Setup (see README): create a service account, share your target Google
Sheet with the service account's email, then point this at:
  - GOOGLE_SHEETS_CREDENTIALS_FILE  (path to the service account JSON key)
  - SPREADSHEET_ID                  (the long ID in the sheet's URL)
"""
import os
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

HEADER_BY_PLATFORM = {
    "google_trends": ["collected_at", "source", "term", "related"],
    "youtube": ["collected_at", "source", "title", "channel", "views", "likes", "comments", "url"],
    "reddit": ["collected_at", "source", "title", "score", "num_comments", "url"],
    "tiktok": ["collected_at", "source", "hashtag", "posts", "rank"],
}


def get_client():
    creds_path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_FILE", "service_account.json")
    if not os.path.exists(creds_path):
        print(f"[sheets] credentials file not found at {creds_path}, skipping Sheets sync")
        return None
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet(client):
    sheet_id = os.environ.get("SPREADSHEET_ID")
    if not sheet_id:
        print("[sheets] SPREADSHEET_ID not set, skipping Sheets sync")
        return None
    return client.open_by_key(sheet_id)


def get_or_create_worksheet(spreadsheet, name, header):
    try:
        ws = spreadsheet.worksheet(name)
    except gspread.exceptions.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=name, rows=1000, cols=max(10, len(header)))
        ws.append_row(header)
    return ws


def write_snapshot(snapshot):
    """Appends every item in a snapshot to its platform's tab. Safe to call
    even when Sheets isn't configured — it just no-ops."""
    client = get_client()
    if client is None:
        return
    spreadsheet = get_spreadsheet(client)
    if spreadsheet is None:
        return

    for platform_data in snapshot["platforms"]:
        platform = platform_data["platform"]
        collected_at = platform_data["collected_at"]
        header = HEADER_BY_PLATFORM.get(platform, ["collected_at", "source", "raw_json"])
        ws = get_or_create_worksheet(spreadsheet, platform, header)

        rows = []
        for item in platform_data["items"]:
            row = [collected_at] + [str(item.get(col, "")) for col in header[1:]]
            rows.append(row)

        if rows:
            ws.append_rows(rows, value_input_option="RAW")

    print(f"[sheets] synced {sum(len(p['items']) for p in snapshot['platforms'])} items to Google Sheets")


def read_platform(platform):
    """Retrieves everything stored for one platform's tab as a list of dicts.
    Used by the dashboard to read history back out of Sheets."""
    client = get_client()
    if client is None:
        return []
    spreadsheet = get_spreadsheet(client)
    if spreadsheet is None:
        return []
    try:
        ws = spreadsheet.worksheet(platform)
    except gspread.exceptions.WorksheetNotFound:
        return []
    return ws.get_all_records()
