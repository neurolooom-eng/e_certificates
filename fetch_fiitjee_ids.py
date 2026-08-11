#!/usr/bin/env python3
"""
Fetch every certificate image in the FIITJEE event's Drive folder and write
fiitjee/certificates.json.

The event folder holds one sub-folder per age category:

    FitJEE/
      Under8_Boys_Certificates/    01_Viyan_B.jpg, 02_Viyaan_Pravera.jpg, ...
      Under8_Girls_Certificates/
      Under11_Boys_Certificates/
      ...

so unlike fetch_drive_ids.py this walks one level down and keys the output by
category. Ranks restart at 1 inside each category.

Two auth options:

  A) Service account / OAuth via google-api-python-client (recommended if you
     already have credentials):
        pip install google-api-python-client google-auth
     then point GOOGLE_CREDS at your service-account JSON, and share the
     folder with that service account's email.

  B) Quick-and-dirty with an API key (only works if the folder is set to
     "Anyone with the link"):
        export DRIVE_API_KEY=your_key
     No install needed beyond `requests`.

Usage:
    python3 fetch_fiitjee_ids.py
"""
import json
import os
import re

# https://drive.google.com/drive/folders/124O6VLbF-KEjU3vkysIAlA5HAFmE2Rhd
ROOT_FOLDER_ID = "124O6VLbF-KEjU3vkysIAlA5HAFmE2Rhd"
OUT = "fiitjee/certificates.json"

EVENT_TITLE = "3rd FIITJEE Tamilnadu State Level Children's Chess Tournament"
EVENT_SUB = "Tamilnadu · 2026 · Certificate of Merit"

FOLDER_MIME = "application/vnd.google-apps.folder"

# Filename pattern: 05_Prathik_Prasanna.jpg
NAME_RE = re.compile(r"^(\d+)_(.+)\.(jpe?g|png|pdf)$", re.IGNORECASE)

# Sub-folder name -> display label. Order here is the order on the page.
CATEGORY_LABELS = [
    ("Under8_Boys_Certificates", "Under 8 Boys"),
    ("Under8_Girls_Certificates", "Under 8 Girls"),
    ("Under11_Boys_Certificates", "Under 11 Boys"),
    ("Under11_Girls_Certificates", "Under 11 Girls"),
    ("Under14_Boys_Certificates", "Under 14 Boys"),
    ("Under14_Girls_Certificates", "Under 14 Girls"),
    ("Under17_Certificates", "Under 17"),
]


def parse(title):
    m = NAME_RE.match(title)
    if not m:
        return None
    rank = int(m.group(1))
    name = m.group(2).replace("_", " ").strip()
    return rank, name


def clean_name(name):
    """Tidy the odd artefact of the source filenames without rewriting names."""
    name = name.replace("_", " ")
    name = re.sub(r"\s*\.\s*", " ", name)      # "Aswanth .G" -> "Aswanth G"
    return re.sub(r"\s{2,}", " ", name).strip()


class Client:
    """Thin wrapper so the two auth paths share one list() call."""

    def __init__(self):
        self.key = os.environ.get("DRIVE_API_KEY")
        if self.key:
            import requests
            self.session = requests.Session()
        else:
            from googleapiclient.discovery import build
            from google.oauth2 import service_account
            creds = service_account.Credentials.from_service_account_file(
                os.environ.get("GOOGLE_CREDS", "service_account.json"),
                scopes=["https://www.googleapis.com/auth/drive.readonly"],
            )
            self.service = build("drive", "v3", credentials=creds)

    def children(self, folder_id):
        """Every non-trashed child of folder_id as (name, id, mimeType)."""
        out = []
        page_token = None
        q = f"'{folder_id}' in parents and trashed=false"
        while True:
            if self.key:
                params = {
                    "q": q,
                    "fields": "nextPageToken, files(id, name, mimeType)",
                    "pageSize": 1000,
                    "key": self.key,
                }
                if page_token:
                    params["pageToken"] = page_token
                r = self.session.get(
                    "https://www.googleapis.com/drive/v3/files", params=params, timeout=30
                )
                r.raise_for_status()
                data = r.json()
            else:
                data = self.service.files().list(
                    q=q,
                    fields="nextPageToken, files(id, name, mimeType)",
                    pageSize=1000,
                    pageToken=page_token,
                ).execute()
            out.extend(
                (f["name"], f["id"], f["mimeType"]) for f in data.get("files", [])
            )
            page_token = data.get("nextPageToken")
            if not page_token:
                break
        return out


def main():
    client = Client()

    subfolders = {
        name: fid
        for name, fid, mime in client.children(ROOT_FOLDER_ID)
        if mime == FOLDER_MIME
    }

    known = {name for name, _ in CATEGORY_LABELS}
    for name in subfolders:
        if name not in known:
            print(f"NOTE: sub-folder not in CATEGORY_LABELS, skipped: {name}")

    categories = []
    for folder_name, label in CATEGORY_LABELS:
        fid = subfolders.get(folder_name)
        if not fid:
            print(f"WARNING: no sub-folder named {folder_name}")
            continue

        records, skipped = {}, []
        for title, file_id, mime in client.children(fid):
            if mime == FOLDER_MIME:
                continue
            parsed = parse(title)
            if not parsed:
                skipped.append(title)
                continue
            rank, name = parsed
            records[rank] = {
                "rank": rank,
                "name": clean_name(name),
                "file_id": file_id,
                "view_url": f"https://drive.google.com/file/d/{file_id}/view",
                "download_url": f"https://drive.google.com/uc?export=download&id={file_id}",
            }

        ordered = [records[r] for r in sorted(records)]
        categories.append({
            "key": folder_name,
            "label": label,
            "folder_id": fid,
            "records": ordered,
        })

        missing = [r for r in range(1, max(records) + 1) if r not in records] if records else []
        print(f"{label:16s} {len(ordered):4d} certificates", end="")
        print(f"  MISSING RANKS: {missing}" if missing else "")
        if skipped:
            print(f"  skipped {len(skipped)} non-matching: {skipped[:5]}"
                  f"{'...' if len(skipped) > 5 else ''}")

    payload = {
        "event": EVENT_TITLE,
        "subtitle": EVENT_SUB,
        "root_folder_id": ROOT_FOLDER_ID,
        "categories": categories,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    total = sum(len(c["records"]) for c in categories)
    print(f"\nWrote {total} certificates across {len(categories)} categories to {OUT}")


if __name__ == "__main__":
    main()
