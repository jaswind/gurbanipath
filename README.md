# Gurbani Path

> A free, non-commercial reading and study aid for Sri Guru Granth Sahib Ji,
> offered with humility and reverence to the worldwide sangat.

🌐 **[gurbanipath.org](https://gurbanipath.org)**

---

## What this is

Gurbani Path is a single-page web application that lets you:

- **Read** all 1,430 angs of Sri Guru Granth Sahib Ji
- **Search** in Roman transliteration or English translation
- **Toggle display** of Gurmukhi script, Roman, English, and citations
- **Bookmark** verses and **mark a reading place** to resume later
- **Use offline** — once loaded, the entire corpus works without internet

It is **not** a replacement for the satikar of a physical Saroop, nor for
traditional scholarly study. It is a reading aid — useful, imperfect, and
offered as seva.

---

## Sources

This project does not generate or alter the text of Sri Guru Granth Sahib Ji.
It bundles freely-available transliterations and translations from these
upstream sources, with gratitude:

- **English translation** — Bhai Sant Singh Khalsa, MD (public domain)
- **Roman transliteration** — Dr. Kulbir Singh Thind (freely shared for
  decades; used widely across the Sikh digital ecosystem)
- **Gurmukhi font** — [Noto Serif Gurmukhi](https://fonts.google.com/noto/specimen/Noto+Serif+Gurmukhi),
  Google Fonts, SIL Open Font License

The Gurmukhi script displayed in the app is **automatically converted**
from a legacy ASCII source to Unicode. The conversion is best-effort and
will contain errors. The Roman and English layers are the canonical
reference; the Gurmukhi is a reading aid we are working to improve over
time. Please report errors via [Issues](../../issues).

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for the full credit list.

---

## License

- **Code:** [GNU Affero General Public License v3.0](LICENSE) (AGPL-3.0)
- **Project content:** [CC BY-SA 4.0](LICENSE-CONTENT)
- **Bundled fonts:** SIL Open Font License (see `public/fonts/OFL.txt`)
- **Upstream translations and transliterations:** Used under their original
  free terms; see CONTRIBUTORS.md.

The AGPL choice means: anyone may use, modify, and redistribute this code,
including running modified versions as a hosted service — but the modified
source must be made available to users of that service. This protects the
work as a public good for the panth.

---

## Project status

This is **Phase 1** of a longer-term project. Current capabilities:

- ✅ Full corpus search (Roman + English)
- ✅ Ang-by-ang reading view
- ✅ Bookmarks and reading-place memory
- ✅ Display preferences (which layers to show)
- ✅ Offline-capable (PWA)
- 🚧 Verified, pothi-grade Unicode Gurmukhi (currently auto-converted)
- 🚧 Audio recitation
- 🚧 Native iOS / Android apps (PWA today)
- 🚧 Punjabi (Gurmukhi) translations / teeka layers

---

## Development

This is a **static site** — no build step, no framework, no server. The
whole app is one large HTML file with the corpus embedded. Deployment is
via [Cloudflare Pages](https://pages.cloudflare.com) on every push to `main`.

```
gurbanipath/
├── public/                  # Everything served at gurbanipath.org
│   ├── index.html           # Landing page
│   ├── app/index.html       # The reading + search app
│   ├── about.html           # What this is, philosophy, disclaimers
│   ├── credits.html         # Sources and contributors
│   ├── privacy.html         # Privacy notes (no tracking, local-only data)
│   ├── feedback.html        # How to send corrections and ideas
│   ├── sw.js                # Service worker for offline use
│   ├── manifest.webmanifest # PWA manifest
│   ├── _headers             # Cloudflare cache + security headers
│   ├── _redirects           # Clean URLs
│   ├── icons/               # Favicons, apple-touch-icon, og-image
│   └── fonts/               # Bundled Noto Gurmukhi (offline-first)
├── _docs/                   # Setup and operations docs (not deployed)
└── .github/                 # Issue templates, workflows
```

To run locally, any static-file server works:

```bash
cd public
python3 -m http.server 8000
# open http://localhost:8000
```

To deploy: see `_docs/DEPLOY.md`.
To update: see `_docs/UPDATING.md`.

---

## Contributing

Contributions are welcomed with gratitude. Most useful contributions:

1. **Verse corrections** — if a Gurmukhi line is wrong, a translation is
   awkward, or a transliteration is misspelled, open an Issue using the
   "Verse correction" template. Include the ang, line, and what should
   change.
2. **Bug reports** — use the "Bug" issue template.
3. **Suggestions** — use the "Suggestion" template, but read the project
   philosophy in `public/about.html` first; some intentional design
   choices (no gamification, no audio yet, no in-app accounts) are
   considered features.

Please be patient with maintainers; this is volunteer seva.

---

## Disclaimer

> Gurbani Path is offered as seva. The text of Sri Guru Granth Sahib Ji
> is sacred; this app is merely a tool for reading and study. The bundled
> translations and transliterations are the work of others, used here
> freely. The Gurmukhi rendering is approximate and will contain errors.
>
> Use this app to support your own reading; do not rely on it as a
> substitute for the physical Saroop, for the traditional teaching of a
> Sikh sangat, or for verified scholarly references.
>
> ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫ਼ਤਹਿ ॥

---

*Built with assistance from Claude (Anthropic) for code generation and
design iteration. All editorial decisions, content selection, and final
review by human sevadars.*
