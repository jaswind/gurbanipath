#!/usr/bin/env python3
"""
translate_corpus.py

Translates the English translation field of every verse in ggs_verses.json
into a target language, using the Claude API. Designed for one-shot batch
translation: output is a new 'translations/<lang>.json' file mapping
verse_index -> translated string, which you then merge into the embedded
corpus during the next build.

Key properties:
  - Resumable: writes after every batch, so a crash mid-run is recoverable.
  - Cost-efficient: uses Claude Haiku and packs ~25 verses per request.
  - Quality-controlled: a fixed system prompt enforces SSK's stylistic
    conventions (untranslated Sikh terms, reverent register, preserved
    verse markers).
  - Language-agnostic: change --lang to spanish, hindi, french, etc.

USAGE
  export ANTHROPIC_API_KEY=sk-ant-...
  pip install anthropic
  python3 translate_corpus.py --lang spanish --test         # 50 verses first
  python3 translate_corpus.py --lang spanish                # full run
  python3 translate_corpus.py --lang spanish --resume       # restart after crash

OUTPUT
  translations/spanish.json    # {"0": "...", "1": "...", ...}
  translations/spanish.log     # one line per batch (start time, count, cost)

To wire the result into the app, edit build_app.py to load this file
alongside ggs_verses.json and add the translation as a fourth field 'sp'
(or similar) on each slimmed verse. The frontend then gets a fourth
display toggle. See README at bottom for the merge snippet.
"""

import argparse, json, os, sys, time
from pathlib import Path

import anthropic  # pip install anthropic

# ---- Configuration -----------------------------------------------------------

# Per-language style guide. Add new entries as you add languages.
STYLE_GUIDES = {
    "spanish": {
        "name": "Spanish",
        "register": (
            "Use a reverent, devotional register. Use 'Tú/Tu' (not 'Usted') "
            "for the divine. Match the intimate-yet-reverent tone of the English."
        ),
    },
    "hindi": {
        "name": "Hindi",
        "register": (
            "Use a reverent, devotional register. Use 'तू' for the divine. "
            "Use Devanagari script."
        ),
    },
    "french": {
        "name": "French",
        "register": (
            "Use a reverent, devotional register. Use 'Tu/Toi' (not 'Vous') "
            "for the divine."
        ),
    },
    # Add more here.
}

# Sikh-specific terms that should NEVER be translated to the target language.
# Sant Singh Khalsa's English already preserves these — we follow suit.
PRESERVE_TERMS = [
    "Naam", "Guru", "Hari", "Hukam", "Gurmukh", "Manmukh", "Maya",
    "Bhagat", "Sangat", "Satsang", "Granth", "Gurbani", "Akal", "Waheguru",
    "Onkar", "Raam", "Gobind", "Govind", "Mohan", "Madho", "Madhav",
    "Khalsa", "Sikh", "Singh", "Kaur", "Sahib",
]

MODEL = "claude-haiku-4-5"          # fast, cheap, more than capable for translation
BATCH_SIZE = 25                       # verses per API call
MAX_TOKENS_PER_BATCH = 4096           # generous; verses average ~30 English words

# ---- Prompt template ---------------------------------------------------------

SYSTEM_PROMPT_TEMPLATE = """\
You are translating Sant Singh Khalsa's English translation of Sri Guru Granth \
Sahib Ji into {LANG_NAME}. You are NOT interpreting, paraphrasing, or generating \
new commentary — only conveying his existing translation in {LANG_NAME}.

STRICT RULES:
1. {REGISTER}
2. Preserve these Sikh-specific terms verbatim (do not translate them): \
{PRESERVE_TERMS}.
3. Preserve verse markers exactly as they appear: ||1||, ||2||rahaa-o||, \
||Pause||, etc. These pass through unchanged in any language.
4. Preserve the capitalization of divine attributes (e.g. "Lord", "Supreme \
Being") in their {LANG_NAME} equivalents.
5. Do NOT add explanations, footnotes, or commentary. Translate only what is \
present.
6. If a line is a single word or fragment, translate it as a single word or \
fragment — do not pad it into a sentence.
7. Match Khalsa's style: literal, devotional, slightly archaic register. He \
often translates each English phrase as its own short sentence; preserve that \
rhythm.

OUTPUT FORMAT:
You will receive a JSON array of English verses, numbered 0..N-1. Return a \
JSON array of the same length, in the same order, with each element being \
the {LANG_NAME} translation of the corresponding English verse. Return ONLY \
the JSON array — no preamble, no markdown fences, no trailing commentary.\
"""

# ---- Main pipeline -----------------------------------------------------------

def build_system_prompt(lang_key: str) -> str:
    guide = STYLE_GUIDES[lang_key]
    return SYSTEM_PROMPT_TEMPLATE.format(
        LANG_NAME=guide["name"],
        REGISTER=guide["register"],
        PRESERVE_TERMS=", ".join(PRESERVE_TERMS),
    )

def translate_batch(client, system_prompt: str, english_batch: list[str]) -> list[str]:
    """Translate one batch of verses. Returns same-length list of translations."""
    user_msg = json.dumps(english_batch, ensure_ascii=False)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS_PER_BATCH,
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = resp.content[0].text.strip()
    # Defensive: strip code fences if the model added them despite instructions
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        if text.startswith("json"):
            text = text[4:].strip()
    out = json.loads(text)
    if len(out) != len(english_batch):
        raise ValueError(
            f"Batch length mismatch: got {len(out)}, expected {len(english_batch)}"
        )
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True, choices=list(STYLE_GUIDES.keys()))
    ap.add_argument("--source", default="ggs_verses.json",
                    help="Path to source corpus JSON")
    ap.add_argument("--outdir", default="translations",
                    help="Where to write the translation JSON")
    ap.add_argument("--test", action="store_true",
                    help="Translate only the first 50 verses (for quality check)")
    ap.add_argument("--resume", action="store_true",
                    help="Skip verses already in the output file")
    args = ap.parse_args()

    if "ANTHROPIC_API_KEY" not in os.environ:
        sys.exit("ERROR: set ANTHROPIC_API_KEY env var")

    client = anthropic.Anthropic()
    system_prompt = build_system_prompt(args.lang)

    src = json.load(open(args.source))
    if args.test:
        src = src[:50]
        print(f"TEST MODE: only first 50 verses")

    outdir = Path(args.outdir); outdir.mkdir(exist_ok=True)
    outfile = outdir / f"{args.lang}.json"
    logfile = outdir / f"{args.lang}.log"

    done = {}
    if args.resume and outfile.exists():
        done = json.load(open(outfile))
        print(f"Resuming: {len(done)} verses already translated")

    todo_indices = [i for i in range(len(src)) if str(i) not in done]
    print(f"Translating {len(todo_indices)} verses to {args.lang} "
          f"({BATCH_SIZE} per batch = {len(todo_indices) // BATCH_SIZE + 1} API calls)")

    log = open(logfile, "a")
    t0 = time.time()
    for batch_start in range(0, len(todo_indices), BATCH_SIZE):
        batch_idx = todo_indices[batch_start : batch_start + BATCH_SIZE]
        english_batch = [src[i]["english"] for i in batch_idx]
        try:
            translations = translate_batch(client, system_prompt, english_batch)
        except Exception as e:
            print(f"  ! Batch {batch_start} failed: {e}; retrying once...")
            time.sleep(2)
            translations = translate_batch(client, system_prompt, english_batch)

        for idx, txt in zip(batch_idx, translations):
            done[str(idx)] = txt

        # Write after every batch for crash-safety
        json.dump(done, open(outfile, "w"), ensure_ascii=False, indent=0)
        elapsed = time.time() - t0
        rate = (batch_start + BATCH_SIZE) / max(elapsed, 0.001)
        eta = (len(todo_indices) - batch_start - BATCH_SIZE) / max(rate, 0.001)
        msg = (f"  ✓ batch ending at index {batch_idx[-1]:>6} | "
               f"{len(done)}/{len(src)} done | "
               f"rate {rate:.1f} verses/s | ETA {eta/60:.1f} min")
        print(msg)
        log.write(msg + "\n"); log.flush()

    log.close()
    print(f"\nDone. Translations at {outfile}")
    print(f"\nTo wire into the app, edit build_app.py:")
    print(f"""
  # After loading ggs_verses.json:
  with open('translations/{args.lang}.json') as f:
      translations_{args.lang} = json.load(f)

  # In the slim_verses list comprehension, add a key:
  slim_verses = [
      {{
          'a': v['ang'],
          'l': v['line'],
          's': src_idx[v['source']],
          'g': v['gurmukhi'],
          'r': v['roman'],
          'e': v['english'],
          '{args.lang[:2]}': translations_{args.lang}.get(str(i), ''),  # NEW
      }}
      for i, v in enumerate(verses)
  ]

  # Then add a fourth display toggle in the app for '{args.lang}'.
""")

if __name__ == "__main__":
    main()
