# Updating the Gurmukhi Converter

This doc supplements `_docs/UPDATING.md`. Use it whenever you're changing
the AnmolLipi → Unicode converter (or anything else that transforms the
embedded corpus at render time).

The converter lives in **two places that must stay in sync**:

1. **`build_app.py`** — the JS converter is a string literal inside the
   `JS = r"""…"""` block (look for `const GUR = (function () {`). This
   is the source of truth for future rebuilds.
2. **`public/app/index.html`** — the same JS converter, baked into the
   deployed single-page app. This is what users actually run.

If you only edit `build_app.py`, the change won't ship until you re-run
the build. If you only edit `public/app/index.html`, the next rebuild
will clobber your fix. Always do both.

---

## The standard converter-update workflow

```bash
cd ~/Calude/Gurbanipath

# 1. Make your converter change in build_app.py (single source of truth)
#    Edit the JS block between "const GUR = (function ()" and the matching ")();"

# 2. Test the converter in isolation BEFORE rebuilding (optional but recommended)
#    Copy just the GUR block into a Node REPL or a quick scratch file:
#      const out = GUR.convert('iqsih prwpiq nwmu qyrw kir ik®pw ijsu dIau ]1]');
#      console.log(out);
#    Verify it renders the expected Unicode.

# 3. Rebuild the deployed HTML
python3 build_app.py
#    This regenerates public/app/index.html with the new converter and
#    the embedded corpus. ~10s.

# 4. Bump the service worker cache version so returning PWA users
#    get the new converter on their next visit (otherwise they're served
#    the old cached /app/ shell for 1 revalidation cycle).
#    Open public/sw.js and bump:
#      const CACHE_VERSION = 'v1';   →   const CACHE_VERSION = 'v2';

# 5. Smoke-test locally
cd public && python3 -m http.server 8000
#    Open http://localhost:8000/app/ in a private window
#    Search for a verse containing the fixed glyph(s); verify it renders correctly
#    Ctrl+C to stop

# 6. Commit and push
cd ..
git add build_app.py public/app/index.html public/sw.js
git commit -m "Fix converter: <what you changed>"
git push
```

Cloudflare Pages picks up the push within ~30 seconds.

---

## Applying a converter patch from a contributor / Claude / external source

When someone hands you a `.patch` file (e.g. `gurmukhi-converter-fix.patch`),
the cleanest path is `git apply`:

```bash
cd ~/Calude/Gurbanipath

# Check the patch applies cleanly (dry run — no changes made)
git apply --check path/to/converter-fix.patch

# If clean, apply it
git apply path/to/converter-fix.patch

# Inspect what changed
git diff
git status
```

If `git apply --check` reports conflicts, your local files diverged from
the patch's base. Two options:

- **Three-way merge** (Git tries to resolve):
  ```bash
  git apply --3way path/to/converter-fix.patch
  ```
- **Manual port**: open the patch in an editor, hand-apply the new
  mappings into your current `build_app.py`, then regenerate via the
  standard workflow above.

A converter patch that modifies the deployed `public/app/index.html`
will only line up if your local copy hasn't been rebuilt against a
different corpus since the patch was generated. If `git apply --check`
fails on `public/app/index.html` but succeeds on `build_app.py`, the
safest move is:

```bash
git apply --include='build_app.py' path/to/converter-fix.patch
python3 build_app.py     # regenerate index.html cleanly
# bump sw.js cache, smoke-test, commit
```

---

## How to debug a misrendered glyph

You spot a glyph rendering wrong on the site (e.g. `ਕਿ®ਪਾ` should be
`ਕ੍ਰਿਪਾ`). Here's how to diagnose:

1. **Find the legacy AnmolLipi character.** The non-Gurmukhi character
   visible on the page (`®` in this case) is the AnmolLipi glyph the
   converter failed on. Note its Unicode codepoint (e.g. U+00AE).

2. **Find verses containing it.** Extract the embedded JSON from
   `public/app/index.html` and search for the character in the `g`
   field:

   ```python
   import json, re
   html = open('public/app/index.html').read()
   m = re.search(r'<script id="verse-data" type="application/json">(.+?)</script>',
                 html, re.DOTALL)
   payload = json.loads(m.group(1))
   for v in payload['verses'][:100]:
       if '®' in v['g']:
           print(f"ang {v['a']} L{v['l']}: legacy={v['g']!r}")
           print(f"               roman ={v['r']!r}")
   ```

3. **Deduce the correct mapping from the Roman transliteration.** The
   Roman field is the canonical reference — work out what Gurmukhi
   syllable the glyph represents (e.g. `ik®pw` aligns to `kirpaa` =
   `ਕ੍ਰਿਪਾ`, so `®` = subjoined ਰ = `੍ਰ`).

4. **Add the mapping to the `subjoiners` map** in `build_app.py`
   (or to one of the other dispatch tables, depending on the glyph
   type — see the structure below).

5. **Audit for completeness.** Run a corpus sweep to confirm no
   other characters fall through unmapped:

   ```python
   from collections import Counter
   counter = Counter()
   for v in payload['verses']:
       for ch in v['g']:
           counter[ch] += 1
   for ch, n in sorted(counter.items(), key=lambda x: ord(x[0])):
       if ord(ch) > 127 or ch in '<>@^':  # focus on non-ASCII oddities
           print(f"U+{ord(ch):04X} {ch!r} count={n}")
   ```

6. **Run the standard workflow** above to ship the fix.

---

## Anatomy of the converter

The JS converter dispatches in this order, top to bottom:

```
1. Word-level digraphs:  '<>' → ੴ,  ']' → ॥,  digits → ੦-੯
2. Whitespace
3. Multi-char digraphs:  'ˆØI' → ੀਂ,  'W' → ਾਂ
4. Pre-vowel sihari:     'i' + consonant [+ subjoiners]
5. Word-start digraphs:  'Aw' → ਆ, 'eI' → ਈ, 'ey' → ਏ
6. After-consonant vowel digraphs:  'au' → ਉ, 'AU' → ਊ, 'AY' → ਐ
7. Independent vowels (only when not after consonant)
8. Vowel matras after consonant (w/y/Y/o/O, u/U/I/O)
9. Subjoined half-forms (lookup table)
10. Bindi/tippi/visarga (M/N/ˆ/`/Ú/µ), drop Ø
11. Plain consonants (lookup table)
12. Pass-through for anything else
```

When adding a new mapping:
- **Half-forms** (੍X glyphs) → add to the `subjoiners` map at the top
- **Low-position vowel marks** (ੁ/ੂ after subjoiners) → same `subjoiners` map
- **Plain consonants** → add to `cmap`
- **Plain vowel matras** → add to `matras`
- **Anything contextual** (digraphs, multi-char sequences) → add an
  explicit `if (c === 'X' && text[i+1] === 'Y')` branch BEFORE the
  table lookups

---

## When the corpus itself changes (not just the converter)

If you ingest a new source — for example, swapping the AnmolLipi-derived
Gurmukhi for BaniDB's verified pothi-grade text (your P0 roadmap item) —
you'll need to:

1. Regenerate `ggs_verses.json` from the new source
2. Update the data-source path at the top of `build_app.py`
3. Run `python3 build_app.py` to rebuild
4. **Bump `CACHE_VERSION` in `public/sw.js`** — critical, because
   returning users have the old corpus cached
5. Update `/about.html` and `/credits.html` to credit the new source
6. Smoke-test, commit, push

---

## Rolling back a converter regression

If a converter change ships and turns out to be wrong, you have two paths:

**Fast (Cloudflare-side rollback):**
Cloudflare Pages → Deployments tab → previous deploy → Rollback. Takes
seconds. Doesn't change your Git history.

**Permanent (Git-side rollback):**
```bash
git revert <bad-commit-sha>
git push
```

Either works. The Cloudflare rollback is faster for a "fix this now"
situation; the Git revert leaves a cleaner audit trail and is preferred
once the immediate pressure is off.
