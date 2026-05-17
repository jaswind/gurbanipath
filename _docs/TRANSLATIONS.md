# Adding a Translation Layer (Spanish, Hindi, etc.)

Translates Sant Singh Khalsa's English (already bundled in your corpus)
into a target language, so non-Punjabi-non-English speakers can read
SGGS in their own language. The English is the canonical reference;
new layers are derivative works of it, not new interpretations of
Gurbani.

## Why this is safe (and licensed)

- **No new interpretation.** The translator is conveying SSK's existing
  English into another language, not generating commentary on Gurbani.
- **License covers it.** Your site's content is CC BY-SA 4.0, which
  explicitly permits derivative works under the same license, with
  attribution.
- **Quality is bounded.** English → Spanish is exactly the kind of task
  modern LLMs are excellent at — far easier than Gurmukhi → anything.

## One-time workflow

```bash
cd ~/Calude/Gurbanipath

# 1. Install the API client and set your key
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...   # get one at console.anthropic.com

# 2. Quality check: translate the first 50 verses and inspect by hand
python3 translate_corpus.py --lang spanish --test
# Output: translations/spanish.json (50 entries)
# Open this and spot-check 10-20 against the English source. Verify:
#   - Naam, Guru, Hari stay untranslated
#   - "Tú" used for the divine (not "Usted")
#   - Verse markers ||1||, ||2|| pass through unchanged
#   - The register feels reverent, not casual
# If anything is off, tune STYLE_GUIDES['spanish']['register'] in the
# script and re-run --test.

# 3. Full run (60,345 verses)
python3 translate_corpus.py --lang spanish
# Takes roughly 1-3 hours wall-clock. Writes incrementally to
# translations/spanish.json so a crash mid-run is recoverable.

# 4. If interrupted, resume from where it stopped
python3 translate_corpus.py --lang spanish --resume

# 5. Wire it into the app — see "Merging into build_app.py" below

# 6. Rebuild and ship
python3 build_app.py
# bump CACHE_VERSION in public/sw.js
git add translations/ build_app.py public/app/index.html public/sw.js
git commit -m "Add Spanish translation layer (derivative of SSK English)"
git push
```

## Cost estimate

At Claude Haiku 4.5 pricing, translating all 60,345 verses runs roughly
**$10–25 total** for one language. Each additional language is the same
one-time cost. This is a one-shot job — not a runtime expense.

## Merging into build_app.py

Add the translation file alongside the existing corpus load, and add
a new field per verse:

```python
# Near the top of build_app.py, after loading ggs_verses.json:

with open(ROOT / 'ggs_verses.json') as f:
    verses = json.load(f)

# NEW: load each available translation
translations = {}
for lang_file in (ROOT / 'translations').glob('*.json'):
    lang_key = lang_file.stem[:2]   # 'spanish' -> 'sp', 'hindi' -> 'hi'
    with open(lang_file) as f:
        translations[lang_key] = json.load(f)

# In the slim_verses comprehension, add one field per language:
slim_verses = [
    {
        'a': v['ang'],
        'l': v['line'],
        's': src_idx[v['source']],
        'g': v['gurmukhi'],
        'r': v['roman'],
        'e': v['english'],
        **{lk: tr.get(str(i), '') for lk, tr in translations.items()},
    }
    for i, v in enumerate(verses)
]
```

Then in the app's frontend JS (`build_app.py` JS template), add a
display toggle and a render layer for each new language, parallel to
how `r` (Roman) and `e` (English) work today. The verse-card template
already has slots for these; you're adding a fourth.

## UI internationalization (separate, smaller task)

Translating the **app chrome** (button labels, "Search", "Bookmarks",
"Mark as reading place", etc.) is a different job — much smaller. The
text strings are in `build_app.py` as plain JS strings; pull them into
a `/translations/ui/{lang}.json` dict and switch based on a user
preference. A volunteer translator can do this in an hour per language;
no API needed.

I'd recommend doing UI i18n in parallel with the first translation
layer, since they ship together as one coherent "Spanish-readable
site."

## Adding languages later

To add Hindi (or anything else), just run:

```bash
python3 translate_corpus.py --lang hindi --test
# review, then full run
python3 translate_corpus.py --lang hindi
```

The script's `STYLE_GUIDES` dict has Spanish, Hindi, and French
pre-configured. To add others (Portuguese, Arabic, Italian), add a
new entry to that dict — name, register description — and rerun.

## Quality control & corrections

Two safeguards:

1. **Public correction channel.** Your existing `feedback.html` already
   accepts verse corrections. When Spanish-speaking users spot bad
   translations, they submit; you fix the entries in `translations/spanish.json`
   by hand and rebuild. The site already shows verse + ang + line, so
   reports are unambiguous.

2. **Side-by-side display.** Because the user can toggle English + Spanish
   on simultaneously, they can spot-check the Spanish against the source
   English in-app. This is much better than hiding the source — it makes
   the translation honest about being derivative.

## Public-facing copy

Once Spanish is live, update `/about.html` and `/credits.html` to make
the derivation honest:

> The Spanish translation is a machine-assisted derivative of Sant Singh
> Khalsa's English translation, generated using a large language model
> with human review for theological terms. The English remains the
> canonical reference layer; the Spanish is offered as accessibility,
> not authority. Corrections welcome via [feedback].

This is the right framing: it doesn't oversell the Spanish, it credits
the English source, and it's a clear invitation for community
improvement over time.

## What NOT to do

- **Don't translate the Gurmukhi or Roman.** Those are not translation
  targets — they're the original (or transliteration of the original).
- **Don't translate verse-by-verse "explanations" or commentary.**
  You're not generating those; if you ever bundle Sahib Singh's
  Punjabi teeka (P4 on your roadmap), it would follow this same
  pipeline — translate his existing Punjabi commentary, don't invent
  new commentary.
- **Don't expose the API at runtime.** This is a build-time batch job.
  Users see the bundled output; no API key sits in the deployed site.
