# Certificate Finder — 2nd International FIDE Rating Chess Tournament (Below 1800, 2026)

A standalone web page to look up a participant's Certificate of Merit by name or
merit rank. Each result links to that recipient's PDF in Google Drive.

## Files
- `index.html` — the page. Fully self-contained (data embedded); open it directly
  or host it.
- `certificates.json` — the rank → name → Drive file-id table the page is built from.
- `build_page.py` — regenerates `index.html` from `certificates.json`.
- `fetch_drive_ids.py` — re-fetches `certificates.json` from the Drive folder
  (for a new event or after re-uploading files).

## Hosting on GitHub Pages
1. Put these files in a repo (root, or a `/docs` folder).
2. Settings → Pages → deploy from branch → pick the folder.
3. Visit the published URL. No API key, no login, nothing else to configure.

## Updating the list later
1. Re-run `fetch_drive_ids.py` (see auth options in the file header) to refresh
   `certificates.json`, **or** edit `certificates.json` by hand.
2. Run `python3 build_page.py` to rebuild `index.html`.
3. Commit and push.

## Notes
- The Drive folder (and the files in it) must be shared so recipients can open
  them — "Anyone with the link → Viewer" is the usual setting for public handout.
- Links open Drive's PDF viewer. To force a direct download instead, the page
  could use the `download_url` field already present in `certificates.json`.
