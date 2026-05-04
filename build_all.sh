#!/usr/bin/env bash
# Convenience script: rebuilds the entire static site.
# Run from the gurbanipath/ root.
set -euo pipefail
echo "Building static pages..."
python3 build_pages.py
echo
echo "Building app..."
python3 build_app.py
echo
echo "Done. Test locally with:"
echo "  cd public && python3 -m http.server 8000"
