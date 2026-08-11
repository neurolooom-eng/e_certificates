#!/usr/bin/env python3
"""
Fetch every PDF in the FIDE event's certificate Drive folder and write
tournaments/fide-below-1800-2026/certificates.json
(rank -> {name, file_id, view_url, download_url}).

Two auth options:

  A) Service account / OAuth via google-api-python-client (recommended if you
     already have credentials):
        pip install google-api-python-client google-auth
     then set CREDS_PATH below to your service-account JSON, and share the
     folder with that service account's email.

  B) Quick-and-dirty with an API key (only works if the folder is set to
     "Anyone with the link"):
        export DRIVE_API_KEY=your_key
     No install needed beyond `requests`.

Usage:
    python3 fetch_drive_ids.py
"""
import json
import os
import re
import sys

FOLDER_ID = "1aHL32jEuGZan2Zj5PpfY3gq9USJ43WW5"
OUT = "tournaments/fide-below-1800-2026/certificates.json"

# Filename pattern: 068_Kapuram_Venkata_Sree_Chetan_Reddy.pdf
NAME_RE = re.compile(r"^(\d+)_(.+)\.pdf$", re.IGNORECASE)


def parse(title):
    m = NAME_RE.match(title)
    if not m:
        return None
    rank = int(m.group(1))
    name = m.group(2).replace("_", " ").strip()
    return rank, name


def via_api_client():
    """Option A: google-api-python-client with a service account."""
    from googleapiclient.discovery import build
    from google.oauth2 import service_account

    creds_path = os.environ.get("GOOGLE_CREDS", "service_account.json")
    creds = service_account.Credentials.from_service_account_file(
        creds_path, scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build("drive", "v3", credentials=creds)

    files = []
    page_token = None
    while True:
        resp = service.files().list(
            q=f"'{FOLDER_ID}' in parents and mimeType='application/pdf' and trashed=false",
            fields="nextPageToken, files(id, name)",
            pageSize=1000,
            pageToken=page_token,
        ).execute()
        files.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return [(f["name"], f["id"]) for f in files]


def via_api_key():
    """Option B: REST + API key (folder must be public)."""
    import requests

    key = os.environ["DRIVE_API_KEY"]
    files = []
    page_token = None
    while True:
        params = {
            "q": f"'{FOLDER_ID}' in parents and mimeType='application/pdf' and trashed=false",
            "fields": "nextPageToken, files(id, name)",
            "pageSize": 1000,
            "key": key,
        }
        if page_token:
            params["pageToken"] = page_token
        r = requests.get("https://www.googleapis.com/drive/v3/files", params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        files.extend(data.get("files", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return [(f["name"], f["id"]) for f in files]


def main():
    if os.environ.get("DRIVE_API_KEY"):
        raw = via_api_key()
    else:
        raw = via_api_client()

    records = {}
    skipped = []
    for title, fid in raw:
        parsed = parse(title)
        if not parsed:
            skipped.append(title)
            continue
        rank, name = parsed
        records[rank] = {
            "rank": rank,
            "name": name,
            "file_id": fid,
            "view_url": f"https://drive.google.com/file/d/{fid}/view",
            "download_url": f"https://drive.google.com/uc?export=download&id={fid}",
        }

    ordered = [records[r] for r in sorted(records)]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(ordered, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(ordered)} records to {OUT}")
    have = set(records)
    missing = [r for r in range(1, max(have) + 1) if r not in have] if have else []
    if missing:
        print(f"WARNING: missing ranks: {missing}")
    if skipped:
        print(f"Skipped {len(skipped)} non-matching files: {skipped[:5]}{'...' if len(skipped) > 5 else ''}")


if __name__ == "__main__":
    main()
