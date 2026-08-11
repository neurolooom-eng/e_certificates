# Certificate Finders

Standalone web pages to look up a participant's Certificate of Merit by name or
merit rank. Each result links to that recipient's file in Google Drive.

| Event | Page | Data | Build | Fetch |
|---|---|---|---|---|
| 2nd International FIDE Rating Chess Tournament (Below 1800, 2026) | `index.html` | `certificates.json` | `build_page.py` | `fetch_drive_ids.py` |
| 3rd FIITJEE Tamilnadu State Level Children's Chess Tournament (2026) | `fiitjee/index.html` | `fiitjee/certificates.json` | `build_fiitjee_page.py` | `fetch_fiitjee_ids.py` |

Both pages are fully self-contained (data embedded) — open them directly or host
them. They share one design; the FIITJEE page adds a category chip row because
its certificates are split across seven age groups, with ranks restarting at 1
inside each group.

## Files
- `index.html` / `fiitjee/index.html` — the pages.
- `certificates.json` — the rank → name → Drive file-id table for the FIDE event.
- `fiitjee/certificates.json` — the same, grouped by age category.
- `build_page.py`, `build_fiitjee_page.py` — regenerate a page from its data file.
- `fetch_drive_ids.py`, `fetch_fiitjee_ids.py` — re-fetch a data file from Drive
  (for a new event or after re-uploading files).

## Hosting on GitHub Pages
1. Put these files in a repo (root, or a `/docs` folder).
2. Settings → Pages → deploy from branch → pick the folder.
3. Visit the published URL. No API key, no login, nothing else to configure.

The FIITJEE page is published at `/fiitjee/` under the same site.

## Updating a list later
1. Re-run the event's fetch script (see auth options in the file header) to
   refresh its data file, **or** edit the JSON by hand.
2. Run the event's build script to rebuild the page:
   `python3 build_page.py` or `python3 build_fiitjee_page.py`.
3. Commit and push.

## Notes
- The Drive folder (and the files in it) must be shared so recipients can open
  them — "Anyone with the link → Viewer" is the usual setting for public handout.
- Links open Drive's PDF viewer. To force a direct download instead, the page
  could use the `download_url` field already present in `certificates.json`.
