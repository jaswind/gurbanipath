# Gurbani Path — Enhancement Roadmap

A focused, solo-developer-realistic backlog. Stories are grouped by tier;
within each tier, ordered by leverage (impact per unit of effort). Time
estimates assume evening + weekend work on a single thread.

## Principles guiding this roadmap

1. **Restraint over feature-creep.** The site's core strength is what it
   doesn't do. Each new feature must earn its place; defaults stay calm.
2. **Bundle, don't generate.** No AI-generated Gurbani, explanations, or
   audio. Use AI only as a build-time translator of existing human work
   (e.g. SSK English → Spanish), with human review.
3. **Seva, not engagement.** No streaks-as-pressure, no notifications,
   no nags, no "you haven't read in 3 days." Habit features stay opt-in
   and gentle.
4. **Community-vetted, not Anthropic-vetted.** Every theological choice
   (which teeka to bundle, which audio reciter to license, what counts
   as "verified" text) defers to gianis and sangat input, not LLMs.

---

## TIER 1 — Foundation (next 1-3 months)

These three close the credibility gap and roughly triple your reachable
audience.

### US-1: Verified pothi-grade Gurmukhi via BaniDB (P0 from roadmap)

> **As** a daily reader or giani evaluating the project's trustworthiness,
> **I want** the Gurmukhi text to match canonical pothi character-for-character,
> **so that** I can read with confidence and recommend the app to sangat.

**Acceptance:**
- Source text matches BaniDB / SikhiToTheMax / SGPC-recognized text
  character-for-character across all 60,345 verses.
- `/about.html` and `/credits.html` credit BaniDB with their preferred
  attribution.
- AnmolLipi converter can be retired (or kept as fallback only).
- The "auto-converted, approximate" disclaimer comes off the site.

**Effort:** 2–3 weekends.
**Dependencies:** Reach BaniDB maintainers; license confirmation (likely
CC BY-SA compatible, but confirm).
**Risk:** License negotiation may take weeks. Mitigate by starting that
conversation now while doing other work.
**Why it's #1:** Every conversation about this app eventually returns to
"but is the Gurmukhi accurate?" Until BaniDB is in, the answer is "mostly,
but the disclaimer is honest." After BaniDB, the answer is yes.

### US-2: Spanish translation layer

> **As** a Spanish-speaking seeker who can't read Gurmukhi or English,
> **I want** to read Sant Singh Khalsa's English translation in Spanish,
> **so that** I can access Gurbani in my mother tongue.

**Acceptance:**
- 60,345 verses translated, available as a 4th display toggle alongside
  Gurmukhi/Roman/English.
- Public-facing copy explicitly labels this as a machine-assisted
  derivative of SSK's English (not authoritative).
- Feedback link visible per-verse for corrections.

**Effort:** 1 weekend (50-verse review + full run + integration).
**Dependencies:** Anthropic API key (~$15-25 one-time cost).
**Risk:** Theological term consistency — mitigated by the `--test` step,
the `PRESERVE_TERMS` list, and the feedback channel.

### US-3: UI internationalization framework

> **As** a non-English speaker,
> **I want** the entire app interface in my language,
> **so that** I can navigate without learning English UI labels first.

**Acceptance:**
- All UI strings extracted into `/translations/ui/{lang}.json` dicts.
- Language switcher in settings persists choice in localStorage.
- Adding a new language is editing one JSON file, no code changes.
- Spanish + Hindi UI shipped alongside US-2/US-5.

**Effort:** 1 weekend for the framework + 1-2 hours per language for the
translation itself (volunteer-friendly task; no API needed).
**Dependencies:** None.
**Risk:** None — this is pure i18n, no theological judgment involved.

---

## TIER 2 — Engagement (3-6 months)

These build habit and reach. None should land before Tier 1.

### US-4: Daily Hukamnama on the home screen (P1 from roadmap)

> **As** a daily-practicing Sikh,
> **I want** to see today's Sri Darbar Sahib Hukamnama when I open the app,
> **so that** I can read it without having to look it up elsewhere.

**Acceptance:**
- Home screen shows today's Hukamnama heading and first 2-3 tukks.
- Tap → opens the full Hukamnama ang with the right verse highlighted.
- Caches the day's Hukamnama for offline access after first fetch.
- Graceful fallback if upstream source is down ("Hukamnama unavailable;
  here's a verse to reflect on" + a deterministic rotation).

**Effort:** 2-3 weekends (data source integration, UI, caching, fallback).
**Dependencies:** A trusted upstream — options: SGPC's official feed,
SikhNet's API, BaniDB's daily Hukamnama endpoint. Pick one, document
why, credit clearly.
**Risk:** Upstream stability; mitigated by the fallback.

### US-5: Hindi translation layer

> **As** a Hindi-speaking diaspora reader,
> **I want** SGGS readable in Hindi,
> **so that** I can study Gurbani in Devanagari.

**Acceptance:** Same as US-2 but Hindi. Same pipeline, just `--lang hindi`.
**Effort:** 1 weekend (the pipeline is already built).
**Dependencies:** US-2 done first (proves the pipeline).

### US-6: Improved PWA install / onboarding

> **As** a first-time visitor,
> **I want** to understand instantly that this is a real app, works offline,
> and is free seva,
> **so that** I don't bounce assuming it's another half-finished web thing.

**Acceptance:**
- First-time visitors see a single, calm onboarding card explaining
  offline support and the "add to home screen" gesture.
- Returning visitors don't see it.
- Install prompt appears at the right moment (after a few minutes of
  use, not immediately).
- Apple Touch Icon and splash screens look polished on iOS.

**Effort:** 1-2 weekends.
**Dependencies:** None.

### US-7: Verse-as-image sharing

> **As** a reader who finds a verse meaningful,
> **I want** to share it as a beautiful image to WhatsApp / Instagram / Signal,
> **so that** the formatting stays intact and others can find the source.

**Acceptance:**
- Long-press a verse → "Share as image" option.
- Generates a branded PNG: verse in Gurmukhi, Roman, English, with ang
  citation and a small "gurbanipath.org" footer.
- Image is the right aspect ratio for WhatsApp status / Instagram story.

**Effort:** 2 weekends (Canvas API rendering, font loading, mobile share
sheet integration).
**Dependencies:** None.

---

## TIER 3 — Stretch (6-12 months)

Higher effort, higher dependency, more risk. Each requires a "go/no-go"
decision based on whether Tier 1+2 succeeded and the audience demands it.

### US-8: Curated audio paath layer (P2 from roadmap, modified)

> **As** a Sikh who learns by listening, or has limited vision,
> **I want** to hear verified human-recorded paath alongside reading,
> **so that** I can listen during commutes or before sleep.

**Acceptance:**
- Each ang has audio that plays in sync with the verse highlighting.
- Pause/play/seek/speed (0.75x / 1x / 1.25x).
- Audio bundled (or CDN-streamed) and clearly attributed to the reciter.
- Permission documented in `/credits.html`.

**Effort:** 3-4 weekends of engineering, but **outreach time dominates** —
weeks to months of conversations with reciters or estates to get
permission. Don't start this until you've got a real "yes" from a
reciter or licensed source.

**Dependencies:** Permission from a respected reciter (Bhai Jarnail Singh
estate, SikhNet's archive, BaniDB's audio collection, etc.) AND audio
hosting capacity (60K verses ≈ 30-50 GB; Cloudflare R2 or similar).

**Risk:** Permissions hardest of all stories on this list. Don't ship
auto-generated TTS as a substitute — that crosses the same line as
AI-generated explanations.

### US-9: Native iOS / Android apps via Capacitor (P3 from roadmap)

> **As** a phone user,
> **I want** to install Gurbani Path from the App Store / Play Store,
> **so that** it feels like a "real app" and shows up in search results.

**Acceptance:**
- Native apps in both stores under the same brand.
- Same offline support, same content.
- Deep links from share-as-image work back into the app.

**Effort:** 2-3 weekends of engineering + 2-4 weeks of app store review
overhead per platform.

**Dependencies:**
- Apple Developer Program ($99/year)
- Google Play Console ($25 one-time)
- A simple Capacitor wrapper around the existing PWA.

**Risk:** App store review processes are unpredictable, especially for
religious content. Allow extra time.

### US-10: Punjabi teeka (Sahib Singh's Darpan) as fifth layer (P4 from roadmap)

> **As** a Punjabi-reading Sikh seeking traditional commentary,
> **I want** to read Sahib Singh's classical Gurbani Darpan alongside the verses,
> **so that** I have authoritative interpretation in Punjabi.

**Acceptance:**
- Toggleable display layer showing Sahib Singh's Punjabi commentary per
  verse / shabad.
- Clearly attributed; original source linked.

**Effort:** 2-4 weeks depending on source format. If clean digital text
exists, integration is straightforward (same pipeline as English/Spanish).
If only PDF exists, OCR + cleanup is multi-week.

**Dependencies:** Digital source for Sahib Singh's Darpan. Punjabi
University Patiala publishes some volumes; check what's available digitally.

**Risk:** Source quality. Better to ship one volume well than all 10
volumes badly.

### US-11: Search refinements

> **As** someone hunting a half-remembered verse,
> **I want** filter chips (raag, mahalla, ang range, bani),
> **so that** I can narrow down faster than scrolling all results.

**Acceptance:**
- Filter chips below the search box: Raag / Author (Mahalla) / Ang range.
- Bani-quick-filters: Japji, Sukhmani, Rehraas, etc.
- Filters persist across searches (or have a "clear all" button).

**Effort:** 1-2 weekends.
**Dependencies:** None — the corpus already has all this metadata.

### US-12: Gentle reading log

> **As** a user building a daily-paath habit,
> **I want** a quiet record of which days I read and roughly how much,
> **so that** I can notice patterns without being nagged.

**Acceptance:**
- A small heatmap on the home screen showing which days I opened the app.
- Optional "today's read: ang 273-275" recap.
- No streaks, no badges, no notifications, no shame on missed days.
- Fully local (localStorage); can be cleared.

**Effort:** 1 weekend.
**Dependencies:** None.
**Risk:** Don't gamify Gurbani. If in doubt, leave the feature out.

---

## Explicitly NOT on the roadmap

- **AI-generated explanations / teeka.** Discussed at length. The site
  positions itself as "a reading aid, not a substitute for traditional
  teaching." Generating commentary on Gurbani crosses that line.
- **AI-generated paath audio (TTS).** Gurmukhi religious pronunciation
  (santhya) is precise; TTS doesn't get it right. Use human reciters or
  don't ship audio.
- **Login accounts, user profiles, cloud sync.** Bookmarks staying local
  is a feature, not a limitation. Account systems pull in moderation,
  legal compliance, and abuse vectors that a one-person seva project
  shouldn't take on.
- **Comments / discussion forums.** The community gathers in gurdwaras
  and on other platforms; the site doesn't need to host that.
- **Advertising, sponsorships, donation prompts.** Code is AGPL-3.0,
  content is CC BY-SA 4.0, project is free seva — keep it that way.

---

## Suggested sequencing for the next ~6 weeks

Given a solo developer with evenings and weekends:

| Week | Focus |
|---|---|
| 1 | Ship converter v2 fix (done with this round). Start BaniDB outreach (write the email, wait for reply). |
| 2 | Spanish translation: `--test` run, review carefully, full run if quality holds. |
| 3 | Wire Spanish into app (build_app.py merge, sw.js bump, ship). Begin UI i18n framework. |
| 4 | Finish UI i18n framework. Translate UI to Spanish. Ship together with Spanish text layer. |
| 5 | Hindi translation full run + UI translation. Ship. |
| 6 | Daily Hukamnama (if BaniDB hasn't responded yet — independent path). |

After this, the roadmap continues into Tier 2 work. Re-evaluate at the
6-week mark based on what feedback comes in from the now-bigger audience.

## How to track this

Don't overthink it. A GitHub Project board with the 12 stories above as
cards, three columns (Backlog / In Progress / Done), is enough. Each
story becomes a labeled issue when work starts so contributors can find
them. No Jira, no sprints, no estimates beyond the rough effort numbers
in this doc.
