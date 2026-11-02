# Release checklist

For EVERY release:

1. Update `README.md` (version badge, "New in vX", changed models/images). If hero images in
   `docs/images/` changed, bump the `?v=N` cache-buster on their links in the README.
2. Regenerate the ModDB description from the README:
   `python tools/make_moddb_description.py` -> writes `docs/moddb_description.html`.
   Images are linked from GitHub (raw.githubusercontent.com, `main`), so push the README and
   `docs/images/` to `main` first, otherwise ModDB shows stale or missing images.
3. Paste the contents of `docs/moddb_description.html` into the ModDB mod page description
   (HTML mode) and save. This must be done for EVERY release, not only big ones.
4. Build the release zip (see the packaging notes) and attach it to the GitHub release and ModDB.
