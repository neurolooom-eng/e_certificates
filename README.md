# Certificate Finders

A small static site for handing out Certificates of Merit. The landing page
lists the tournaments; each tournament has its own page where a participant
looks themselves up by name or rank and opens their certificate in Google Drive.

```
index.html                                          Tournaments landing page
tournaments/fide-below-1800-2026/index.html         2nd International FIDE Rating
tournaments/fiitjee-tn-children-2026/index.html     3rd FIITJEE Tamilnadu State Level
```

Every page embeds its data inline, so each one is fully self-contained — open it
directly or host it. No API key, no login, no build step at view time.

## Files
- `build_site.py` — builds the landing page and every tournament page. The
  `TOURNAMENTS` list at the top is the registry of events.
- `tournaments/<slug>/certificates.json` — one event's rank → name → Drive
  file-id table. Two shapes are supported: a flat list (one ranking) or
  `{"categories": [...]}` (ranks restart at 1 inside each category).
- `fetch_drive_ids.py` — fetches the FIDE event's data from a flat Drive folder
  of PDFs.
- `fetch_fiitjee_ids.py` — fetches the FIITJEE event's data, walking one level
  down into its per-age-category sub-folders of images.

The two pages share one design. A categorised event's page grows a category chip
row and labels each row with its category, since otherwise its seven "1st" rows
would be indistinguishable.

## Hosting on GitHub Pages
1. Put these files in a repo (root, or a `/docs` folder).
2. Settings → Pages → deploy from branch → pick the folder.
3. Visit the published URL. Tournament pages live at `/tournaments/<slug>/`.

## Updating a list later
1. Re-run the event's fetch script (see auth options in the file header) to
   refresh its `certificates.json`, **or** edit that file by hand.
2. Run `python3 build_site.py` to rebuild every page.
3. Commit and push.

## Adding a tournament
1. Upload the certificates to Drive, named `NN_First_Last.pdf` (or `.jpg`), where
   `NN` is the rank. Group them in per-category sub-folders if the event has
   categories.
2. Write a fetch script for it, or copy the closer of the two existing ones and
   change `FOLDER_ID`/`ROOT_FOLDER_ID` and `OUT`.
3. Add an entry to `TOURNAMENTS` in `build_site.py`, then run it.

## Notes
- The Drive folder (and the files in it) must be shared so recipients can open
  them — "Anyone with the link → Viewer" is the usual setting for public handout.
- Links open Drive's viewer. To force a direct download instead, the page could
  use the `download_url` field already present in each `certificates.json`.
- The number in a filename is taken as the participant's rank and shown with an
  ordinal suffix (`1st`, `2nd`, …). Where the numbers are serial rather than
  placings, that label is worth revisiting.
