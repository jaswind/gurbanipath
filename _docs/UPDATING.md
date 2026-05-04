# Updating Gurbani Path

Once deployed, updates are dead simple: **commit and push**. Cloudflare
Pages watches the GitHub repo and redeploys on every push to `main`.

## The standard update flow

```bash
# 1. Make your changes locally
cd path/to/gurbanipath
# (edit files in public/ as needed)

# 2. Test locally before pushing
cd public
python3 -m http.server 8000
# open http://localhost:8000 — verify nothing is broken

# 3. Commit and push
cd ..
git add .
git commit -m "Fix transliteration on ang 726"
git push
```

Within ~30 seconds, the change is live on `gurbanipath.org`.

## Updating the corpus

The corpus is **embedded** in `public/app/index.html` as a JSON blob
inside a `<script>` tag. To regenerate it (e.g., after fixing the
parser or improving the Gurmukhi converter):

1. Re-run the build script that produced the original `public/app/index.html`
   (the one whose name was `build_saroop_full.py` during development;
   keep this script outside `public/` if you want — it's a build tool,
   not a deployable asset)
2. Output the new `public/app/index.html`
3. Bump the cache version in `public/sw.js`:
   ```js
   const CACHE_VERSION = 'v2';   // bump from v1 → v2
   ```
   This forces all returning visitors to re-cache the new app HTML
   instead of serving the old version from disk.
4. Commit and push.

Returning users will receive the updated app on their next visit;
the service worker upgrades the cache transparently in the background.

## Updating styles or copy

Most edits will be to:
- `public/index.html` — landing page copy
- `public/about.html` — philosophy and disclaimers
- `public/credits.html` — adding new contributors
- `public/feedback.html` — channels and forms
- `public/app/index.html` — the app itself

These don't require a `sw.js` version bump because the service worker
uses `network-first` for HTML files. They take effect immediately
on next page load.

## Rolling back a bad deploy

In Cloudflare Pages dashboard → your project → **Deployments** tab.

Every push creates a new deployment. To roll back:
1. Find the last known-good deployment in the list
2. Click the `…` menu → **Rollback to this deployment**

Your site is reverted in seconds.

## Versioning releases

For a small project, simple Git history is enough. Once you're shipping
significant changes, consider Git tags:

```bash
git tag -a v1.0.0 -m "Phase 1 launch"
git push --tags
```

GitHub will list these on the **Releases** page, which is a nice
human-readable history.

## Updating dependencies

There are no JavaScript dependencies — the app is vanilla JS. The
only external dependencies are:

- **Noto Serif Gurmukhi font** — bundled in `public/fonts/`. To
  update, download the latest from
  https://github.com/google/fonts/tree/main/ofl/notoserifgurmukhi
  and replace the file. Update `public/fonts/OFL.txt` if the license
  text changes (rare).
- **Source corpus text** — see "Updating the corpus" above.

Nothing else.

## Continuous improvement loop

A healthy update rhythm for the first year:

- **Daily:** read incoming Issues; thank people; close obvious dupes
- **Weekly:** apply easy verse corrections; ship a deploy
- **Monthly:** review what's been requested; pick one larger feature to
  build; ship deploys as you go
- **Quarterly:** check the Cloudflare Analytics dashboard; review
  whether anything needs hardening; thank major contributors in CONTRIBUTORS.md
