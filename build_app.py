#!/usr/bin/env python3
"""
Build the full saroop.html with:
- All 1,430 angs / 60K verses embedded
- Token inverted index for fast search at scale
- Improved ranking (phrase > all-tokens > partial > single-word)
- Display toggles (Gurmukhi / Roman / English) saved to localStorage
- AnmolLipi -> Unicode Gurmukhi converter (best-effort)
- Same mobile-first 'Pocket Saroop' aesthetic as before
"""
from pathlib import Path
import json

ROOT = Path('/home/claude/ggs')
OUT  = Path('/home/claude/gurbanipath/public/app/index.html')
OUT.parent.mkdir(parents=True, exist_ok=True)

# Load and slim the corpus (deduplicate sources to save space)
with open(ROOT / 'ggs_verses.json') as f:
    verses = json.load(f)

sources = sorted({v['source'] for v in verses})
src_idx = {s: i for i, s in enumerate(sources)}

slim_verses = [
    {
        'a': v['ang'],
        'l': v['line'],
        's': src_idx[v['source']],
        'g': v['gurmukhi'],
        'r': v['roman'],
        'e': v['english'],
    }
    for v in verses
]

payload = {'sources': sources, 'verses': slim_verses}
data_json = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
print(f"Corpus payload: {len(data_json) / (1024 * 1024):.2f} MB")

CSS = r"""
:root {
  --paper:        #f4eee2;
  --paper-soft:   #f8f3e7;
  --surface:      #fbf7ee;
  --surface-up:   #fdfaf2;
  --ink:          #1c1814;
  --ink-2:        #3d342a;
  --ink-3:        #6b5c47;
  --ink-4:        #9d8e72;
  --rule:         #d4c8a8;
  --rule-soft:    #e8dec4;
  --hairline:     #e8dfc6;
  --accent:       #9b5a1a;
  --accent-soft:  #c1864a;
  --accent-bg:    rgba(193, 134, 74, 0.13);
  --accent-bg-strong: rgba(193, 134, 74, 0.22);
  --highlight:    rgba(193, 134, 74, 0.22);
  --shadow-soft:  0 1px 0 rgba(28, 24, 20, 0.04), 0 4px 12px rgba(28, 24, 20, 0.04);
  --shadow-up:    0 -1px 0 rgba(28, 24, 20, 0.06), 0 -4px 16px rgba(28, 24, 20, 0.06);
  --font-display: 'Cormorant Garamond', Georgia, serif;
  --font-body:    'Source Serif 4', 'Source Serif Pro', Georgia, serif;
  --font-ui:      'Albert Sans', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', ui-monospace, monospace;
  --font-gurmukhi:'Noto Serif Gurmukhi', 'Noto Sans Gurmukhi', serif;
  --tab-h: 64px; --header-h: 56px;
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-top: env(safe-area-inset-top, 0px);
}
* { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
html, body { margin: 0; padding: 0; height: 100%; overscroll-behavior-y: contain; }
body {
  font-family: var(--font-body); font-size: 16px; line-height: 1.55;
  color: var(--ink); background: var(--paper);
  -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}
body::before {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0; opacity: 0.6;
  background-image:
    radial-gradient(circle at 17% 22%, rgba(60, 40, 0, 0.02) 1px, transparent 1.4px),
    radial-gradient(circle at 73% 51%, rgba(60, 40, 0, 0.018) 1px, transparent 1.4px),
    radial-gradient(circle at 38% 84%, rgba(60, 40, 0, 0.02) 1px, transparent 1.4px);
  background-size: 200px 200px, 280px 280px, 240px 240px;
}
button { font-family: inherit; cursor: pointer; border: none; background: none; padding: 0; color: inherit; }
input { font-family: inherit; }

/* Loading screen */
.loader {
  position: fixed; inset: 0; z-index: 1000;
  background: var(--paper);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  gap: 14px;
  transition: opacity 0.4s; opacity: 1;
}
.loader.hidden { opacity: 0; pointer-events: none; }
.loader .ornament {
  font-family: var(--font-display); font-size: 36px;
  color: var(--accent); letter-spacing: 0.6em; padding-left: 0.6em;
}
.loader .text {
  font-family: var(--font-display); font-style: italic;
  color: var(--ink-3); font-size: 16px;
}

#app {
  position: relative; z-index: 1;
  min-height: 100vh; min-height: 100dvh;
  max-width: 480px; margin: 0 auto;
  padding-bottom: calc(var(--tab-h) + var(--safe-bottom));
  padding-top: var(--safe-top);
}

.app-header {
  height: var(--header-h);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 18px;
  position: sticky; top: var(--safe-top); z-index: 10;
  background: linear-gradient(to bottom, var(--paper) 70%, rgba(244, 238, 226, 0));
}
.app-header .brand {
  font-family: var(--font-display); font-style: italic; font-weight: 500;
  font-size: 19px; color: var(--ink);
}
.app-header .brand .punj {
  font-family: var(--font-gurmukhi); font-style: normal;
  color: var(--accent); margin-right: 6px; font-size: 18px;
}
.app-header .menu-icon { width: 22px; height: 22px; color: var(--ink-3); }

.view { display: none; padding: 8px 18px 32px; animation: viewfade 0.3s ease-out; }
.view.active { display: block; }
@keyframes viewfade { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

.eyebrow {
  font-family: var(--font-ui); font-size: 10px;
  letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--accent); font-weight: 500;
}

.verse-of-day {
  margin: 24px 0 36px; padding: 32px 4px; cursor: pointer;
  transition: opacity 0.15s;
}
.verse-of-day:active { opacity: 0.65; }
.verse-of-day .ornament {
  font-family: var(--font-display); font-size: 28px; color: var(--accent);
  text-align: center; margin-bottom: 18px;
  letter-spacing: 0.4em; padding-left: 0.4em;
}
.verse-of-day .label { text-align: center; margin-bottom: 24px; }
.verse-of-day .gurmukhi {
  font-family: var(--font-gurmukhi); font-weight: 500;
  font-size: 22px; line-height: 1.55; color: var(--ink);
  margin: 0 0 16px;
}
.verse-of-day .roman {
  font-family: var(--font-display); font-style: italic; font-weight: 500;
  font-size: 22px; line-height: 1.4; color: var(--ink); margin: 0 0 14px;
}
.verse-of-day .english {
  font-family: var(--font-body); font-size: 16px; line-height: 1.65;
  color: var(--ink-2); margin: 0 0 22px;
}
.verse-of-day .citation {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--ink-4); text-align: center;
  border-top: 1px solid var(--rule-soft); padding-top: 14px;
}
.verse-of-day .citation .dot { color: var(--accent); margin: 0 6px; }

/* Resume card - "continue reading from here" bookmark */
.resume-card {
  position: relative;
  margin: 14px 0 18px;
  padding: 18px 18px 16px 22px;
  background: var(--surface-up);
  border: 1px solid var(--rule);
  border-left: 4px solid var(--accent);
  border-radius: 6px;
  box-shadow: var(--shadow-soft);
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
  -webkit-user-select: none; user-select: none;
}
.resume-card:active { background: var(--surface); transform: scale(0.99); }
.resume-eyebrow-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 10px;
}
.resume-eyebrow {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: var(--font-ui); font-size: 10px; font-weight: 600;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--accent);
}
.resume-eyebrow svg { width: 12px; height: 12px; }
.resume-clear {
  width: 26px; height: 26px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%; color: var(--ink-4);
  transition: background 0.12s;
}
.resume-clear:active { background: var(--rule-soft); }
.resume-preview {
  margin: 0 0 10px;
  font-family: var(--font-display); font-style: italic;
  font-size: 17px; line-height: 1.4; color: var(--ink);
}
.resume-meta {
  display: flex; justify-content: space-between; align-items: center;
  flex-wrap: wrap; gap: 6px;
  font-family: var(--font-mono); font-size: 9.5px;
  letter-spacing: 0.16em; text-transform: uppercase; color: var(--ink-4);
}
.resume-meta .resume-cite { color: var(--accent); }
.resume-meta .resume-time { font-style: normal; }

.section-title {
  font-family: var(--font-ui); font-size: 11px; font-weight: 600;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--ink-3);
  margin: 36px 0 14px;
  display: flex; align-items: center; gap: 10px;
}
.section-title::before, .section-title::after {
  content: ""; flex: 1; height: 1px; background: var(--rule-soft);
}

.quick-list { display: grid; gap: 6px; }
.quick-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 16px;
  background: var(--surface); border: 1px solid var(--hairline);
  border-radius: 4px; text-align: left; width: 100%;
  transition: background 0.15s, transform 0.1s;
}
.quick-item:active { transform: scale(0.98); background: var(--surface-up); }
.quick-item .label { font-family: var(--font-display); font-style: italic; font-size: 17px; color: var(--ink); }
.quick-item .meta { font-family: var(--font-mono); font-size: 10px; color: var(--ink-4); letter-spacing: 0.1em; }

/* Search */
.search-shell { margin: 12px 0 8px; position: relative; }
.search-input {
  width: 100%;
  font-family: var(--font-display); font-style: italic; font-size: 19px;
  padding: 16px 44px 16px 50px;
  background: var(--surface-up); border: 1px solid var(--rule);
  border-radius: 6px; color: var(--ink);
  box-shadow: var(--shadow-soft); outline: none;
  transition: border-color 0.18s, box-shadow 0.18s;
  -webkit-appearance: none;
}
.search-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-bg); }
.search-input::placeholder { color: var(--ink-4); }
.search-icon {
  position: absolute; left: 18px; top: 50%; transform: translateY(-50%);
  width: 18px; height: 18px; color: var(--ink-4); pointer-events: none;
}
.search-clear {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  width: 24px; height: 24px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%; color: var(--ink-4);
  opacity: 0; pointer-events: none; transition: opacity 0.15s;
}
.search-clear.visible { opacity: 1; pointer-events: auto; }
.search-clear:active { background: var(--rule-soft); }

.field-toggle {
  display: flex; gap: 4px; margin: 12px 0 0; padding: 4px;
  background: var(--surface); border: 1px solid var(--hairline);
  border-radius: 999px; width: fit-content;
}
.field-toggle button {
  font-family: var(--font-ui); font-size: 11px; font-weight: 500;
  letter-spacing: 0.1em; text-transform: uppercase;
  padding: 7px 14px; border-radius: 999px; color: var(--ink-3);
  transition: all 0.15s;
}
.field-toggle button.active { background: var(--ink); color: var(--paper); }

.search-status {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--ink-4); margin: 22px 0 8px;
  display: flex; justify-content: space-between;
}

.verse-list { margin: 0; padding: 0; list-style: none; }
.verse-card {
  padding: 20px 0; border-bottom: 1px solid var(--hairline);
  cursor: pointer; -webkit-user-select: none; user-select: none;
  transition: opacity 0.15s, background 0.18s;
  position: relative;
}
.verse-card:active { opacity: 0.55; }
.verse-card:last-child { border-bottom: none; }
.verse-card .meta {
  display: flex; justify-content: space-between; align-items: baseline;
  margin-bottom: 10px;
  font-family: var(--font-mono); font-size: 9.5px;
  letter-spacing: 0.18em; text-transform: uppercase; color: var(--ink-4);
}
.verse-card .meta .cite { color: var(--accent); font-weight: 500; }
.verse-card .gurmukhi {
  font-family: var(--font-gurmukhi); font-size: 17px;
  line-height: 1.6; color: var(--ink); margin: 0 0 8px;
}
.verse-card .roman {
  font-family: var(--font-display); font-style: italic;
  font-size: 17px; line-height: 1.45;
  color: var(--ink); margin: 0 0 8px;
}
.verse-card .english {
  font-family: var(--font-body); font-size: 14.5px; line-height: 1.55;
  color: var(--ink-2); margin: 0;
}
.verse-card.matched {
  background: linear-gradient(90deg, var(--accent-bg-strong) 0%, var(--accent-bg) 30%, transparent 80%);
  margin-left: -18px; margin-right: -18px;
  padding-left: 18px; padding-right: 18px;
  border-left: 3px solid var(--accent);
  border-radius: 0 6px 6px 0;
}
.verse-card.matched .meta .cite { color: var(--accent); font-weight: 600; }
.verse-card .bookmark-mark { color: var(--accent); margin-left: 4px; }

mark { background: var(--highlight); color: inherit; padding: 0 2px; border-radius: 1px; }

.empty { text-align: center; padding: 80px 24px; color: var(--ink-4); }
.empty .ornament {
  font-family: var(--font-display); font-size: 28px; color: var(--accent);
  letter-spacing: 0.6em; padding-left: 0.6em; margin-bottom: 18px;
}
.empty .text {
  font-family: var(--font-display); font-style: italic; font-size: 17px;
  line-height: 1.5; color: var(--ink-3); max-width: 280px; margin: 0 auto;
}
.hints { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0 4px; }
.hint {
  font-family: var(--font-display); font-style: italic; font-size: 14px;
  color: var(--accent); border-bottom: 1px dotted var(--accent-soft);
  padding: 2px 0; transition: color 0.15s;
}
.hint:active { color: var(--ink); border-bottom-color: var(--ink); }

.bottom-tabs {
  position: fixed; bottom: 0; left: 0; right: 0;
  height: calc(var(--tab-h) + var(--safe-bottom));
  padding-bottom: var(--safe-bottom);
  border-top: 1px solid var(--rule-soft);
  box-shadow: var(--shadow-up);
  display: flex; z-index: 100;
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  background: rgba(248, 243, 231, 0.92);
}
.bottom-tabs .tab {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 4px;
  color: var(--ink-4);
  font-family: var(--font-ui); font-size: 10px;
  letter-spacing: 0.12em; text-transform: uppercase; font-weight: 500;
  transition: color 0.15s;
  -webkit-user-select: none; user-select: none;
}
.bottom-tabs .tab svg { width: 20px; height: 20px; }
.bottom-tabs .tab.active { color: var(--ink); }
.bottom-tabs .tab.active .tab-icon-bg { background: var(--accent-bg); }
.tab-icon-bg {
  width: 36px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 999px; transition: background 0.18s;
}

.overlay {
  position: fixed; inset: 0;
  background: var(--paper); z-index: 200;
  display: flex; flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.32s cubic-bezier(0.32, 0.72, 0, 1);
  overflow: hidden;
}
.overlay.open { transform: translateX(0); }

.overlay-header {
  height: var(--header-h);
  padding-top: var(--safe-top); padding-left: 6px; padding-right: 6px;
  display: flex; align-items: center;
  background: var(--paper);
  border-bottom: 1px solid var(--hairline);
  flex-shrink: 0; gap: 2px;
}
.overlay-back {
  display: flex; align-items: center; gap: 2px;
  padding: 8px 6px 8px 8px;
  color: var(--accent);
  font-family: var(--font-ui); font-size: 14px; font-weight: 500;
  flex-shrink: 0;
}
.overlay-back svg { width: 18px; height: 18px; }
.ang-nav { flex: 1; display: flex; align-items: center; justify-content: center; gap: 4px; }
.ang-nav-btn {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px; color: var(--ink-3);
  transition: all 0.12s;
}
.ang-nav-btn svg { width: 18px; height: 18px; }
.ang-nav-btn:active { background: var(--rule-soft); color: var(--ink); }
.ang-nav-btn:disabled { opacity: 0.25; pointer-events: none; }
.ang-title {
  font-family: var(--font-mono); font-size: 11px;
  letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--ink); font-weight: 500;
  min-width: 70px; text-align: center;
  cursor: pointer;
}
.overlay-icon-btn {
  width: 38px; height: 38px;
  display: flex; align-items: center; justify-content: center;
  color: var(--ink-3); border-radius: 8px;
  transition: background 0.12s;
  flex-shrink: 0;
}
.overlay-icon-btn svg { width: 20px; height: 20px; }
.overlay-icon-btn:active { background: var(--rule-soft); }
.overlay-icon-btn.active { color: var(--accent); }

.overlay-content {
  flex: 1; overflow-y: auto; padding: 24px 24px 80px;
  -webkit-overflow-scrolling: touch;
}
.ang-page-header {
  text-align: center; padding: 8px 0 24px;
  border-bottom: 1px solid var(--rule-soft); margin-bottom: 8px;
}
.ang-page-header .ornament {
  font-family: var(--font-display); font-size: 22px; color: var(--accent);
  letter-spacing: 0.4em; padding-left: 0.4em; margin-bottom: 8px;
}
.ang-page-header .label {
  font-family: var(--font-display); font-style: italic; font-size: 22px;
  color: var(--ink); margin: 0 0 4px;
}
.ang-page-header .source {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.18em; text-transform: uppercase; color: var(--ink-4);
}

.ang-page .verse-card { cursor: default; }
.ang-page .verse-card .gurmukhi { font-size: 19px; line-height: 1.65; }
.ang-page .verse-card .roman { font-size: 18px; line-height: 1.5; }
.ang-page .verse-card .english { font-size: 15px; line-height: 1.6; }

/* hide hidden fields */
body.hide-gurmukhi .verse-card .gurmukhi,
body.hide-gurmukhi .verse-of-day .gurmukhi { display: none; }
body.hide-roman .verse-card .roman,
body.hide-roman .verse-of-day .roman { display: none; }
body.hide-english .verse-card .english,
body.hide-english .verse-of-day .english { display: none; }
body.hide-citation .verse-card .meta,
body.hide-citation .verse-of-day .citation { display: none; }

/* Action sheet */
.action-sheet {
  position: fixed; inset: 0; z-index: 400;
  display: flex; align-items: flex-end; pointer-events: none;
}
.action-sheet[hidden] { display: none !important; }
.action-sheet-backdrop {
  position: absolute; inset: 0;
  background: rgba(28, 24, 20, 0.4);
  opacity: 0; transition: opacity 0.2s; pointer-events: auto;
}
.action-sheet.open .action-sheet-backdrop { opacity: 1; }
.action-sheet-content {
  position: relative; width: 100%; max-width: 480px;
  margin: 0 auto;
  background: var(--surface-up);
  border-top-left-radius: 14px; border-top-right-radius: 14px;
  padding: 8px 8px calc(8px + var(--safe-bottom));
  transform: translateY(110%);
  transition: transform 0.28s cubic-bezier(0.32, 0.72, 0, 1);
  pointer-events: auto;
  box-shadow: 0 -8px 32px rgba(28, 24, 20, 0.18);
}
.action-sheet.open .action-sheet-content { transform: translateY(0); }
.action-sheet-handle {
  width: 40px; height: 4px; background: var(--rule);
  border-radius: 2px; margin: 8px auto 12px;
}
.action-sheet-preview {
  font-family: var(--font-display); font-style: italic; font-size: 15px;
  color: var(--ink-2);
  padding: 0 16px 14px; margin: 0 4px 8px;
  border-bottom: 1px solid var(--rule-soft);
  text-align: center; line-height: 1.4;
  max-height: 80px; overflow: hidden;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
}
.action-sheet-preview-cite {
  display: block;
  font-family: var(--font-mono); font-style: normal;
  font-size: 9.5px; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--accent);
  margin-bottom: 8px;
}
.action-sheet-item {
  display: flex; align-items: center; gap: 14px; width: 100%;
  padding: 14px 18px;
  font-family: var(--font-ui); font-size: 15px;
  color: var(--ink); border-radius: 10px;
  text-align: left; transition: background 0.12s;
}
.action-sheet-item svg { width: 20px; height: 20px; color: var(--ink-3); flex-shrink: 0; }
.action-sheet-item:active { background: var(--rule-soft); }
.action-sheet-item.active-state svg { color: var(--accent); }
.action-sheet-item .check {
  margin-left: auto; color: var(--accent); font-weight: 700; font-size: 18px;
}
.action-sheet-cancel {
  margin-top: 6px; justify-content: center;
  font-weight: 500; background: var(--surface); color: var(--ink-2);
}
.action-sheet-divider {
  height: 1px; background: var(--rule-soft);
  margin: 6px 12px;
}
.action-sheet-section {
  font-family: var(--font-ui); font-size: 10px; font-weight: 600;
  letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--ink-4);
  padding: 8px 18px 4px;
}

.toast {
  position: fixed;
  bottom: calc(var(--tab-h) + var(--safe-bottom) + 16px);
  left: 50%; transform: translateX(-50%) translateY(20px);
  background: var(--ink); color: var(--paper-soft);
  font-family: var(--font-ui); font-size: 13px;
  padding: 10px 18px; border-radius: 999px;
  opacity: 0; pointer-events: none;
  transition: opacity 0.2s, transform 0.2s;
  z-index: 500; white-space: nowrap;
}
.toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }

/* Update-available banner — shown when a new SW version takes over.
   Subtle, dismissible; the user controls when the refresh happens. */
.update-banner {
  position: fixed;
  top: calc(var(--safe-top) + 8px);
  left: 50%; transform: translateX(-50%) translateY(-12px);
  display: flex; align-items: center; gap: 12px;
  background: var(--surface-up);
  border: 1px solid var(--rule);
  border-radius: 999px;
  padding: 8px 8px 8px 16px;
  box-shadow: 0 8px 24px rgba(28, 24, 20, 0.12);
  font-family: var(--font-ui); font-size: 13px;
  color: var(--ink-2);
  opacity: 0; pointer-events: none;
  transition: opacity 0.25s, transform 0.25s;
  z-index: 600;
  max-width: calc(100vw - 32px);
}
.update-banner.show { opacity: 1; transform: translateX(-50%) translateY(0); pointer-events: auto; }
.update-banner-refresh {
  background: var(--accent); color: var(--paper);
  border: none; border-radius: 999px;
  padding: 6px 14px;
  font: inherit; font-weight: 500;
  cursor: pointer;
}
.update-banner-refresh:active { background: var(--accent-soft); }
.update-banner-dismiss {
  background: transparent; border: none;
  color: var(--ink-4); cursor: pointer;
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%; font-size: 18px; line-height: 1;
}
.update-banner-dismiss:active { background: var(--rule-soft); }

/* Ang-jump dialog */
.ang-jump-popover {
  position: absolute; top: calc(var(--header-h) + 6px);
  left: 50%; transform: translateX(-50%) scaleY(0.95);
  transform-origin: top center;
  background: var(--surface-up);
  border: 1px solid var(--rule);
  border-radius: 10px;
  padding: 14px 16px;
  box-shadow: 0 12px 32px rgba(28, 24, 20, 0.16);
  z-index: 250;
  opacity: 0; pointer-events: none;
  transition: opacity 0.18s, transform 0.18s;
  display: flex; align-items: center; gap: 8px;
}
.ang-jump-popover.open { opacity: 1; pointer-events: auto; transform: translateX(-50%) scaleY(1); }
.ang-jump-popover label {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--ink-4);
}
.ang-jump-popover input {
  width: 80px; padding: 6px 10px;
  background: var(--paper); border: 1px solid var(--rule);
  border-radius: 6px; color: var(--ink);
  font-family: var(--font-mono); font-size: 14px;
  text-align: center; outline: none;
}
.ang-jump-popover input:focus { border-color: var(--accent); }
.ang-jump-popover button {
  padding: 6px 14px;
  background: var(--ink); color: var(--paper);
  font-family: var(--font-ui); font-size: 12px; font-weight: 500;
  letter-spacing: 0.1em; text-transform: uppercase;
  border-radius: 6px;
}

/* Info sheet (About / site links) — modal dialog */
.info-sheet {
  position: fixed; inset: 0; z-index: 450;
  display: flex; align-items: center; justify-content: center;
  pointer-events: none;
}
.info-sheet[hidden] { display: none !important; }
.info-sheet-backdrop {
  position: absolute; inset: 0;
  background: rgba(28, 24, 20, 0.55);
  opacity: 0; transition: opacity 0.25s; pointer-events: auto;
  backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
}
.info-sheet.open .info-sheet-backdrop { opacity: 1; }
.info-sheet-content {
  position: relative;
  width: calc(100% - 32px); max-width: 420px;
  max-height: calc(100vh - 64px);
  overflow-y: auto;
  background: var(--paper);
  border: 1px solid var(--rule);
  border-radius: 14px;
  padding: 36px 28px 28px;
  transform: scale(0.96) translateY(8px); opacity: 0;
  transition: transform 0.25s cubic-bezier(0.32, 0.72, 0, 1), opacity 0.2s;
  pointer-events: auto;
  box-shadow: 0 24px 64px rgba(28, 24, 20, 0.22);
  -webkit-overflow-scrolling: touch;
}
.info-sheet.open .info-sheet-content { transform: scale(1) translateY(0); opacity: 1; }

.info-sheet-close {
  position: absolute; top: 12px; right: 12px;
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%; color: var(--ink-3);
  transition: background 0.12s, color 0.12s;
}
.info-sheet-close svg { width: 20px; height: 20px; }
.info-sheet-close:active { background: var(--rule-soft); color: var(--ink); }

.info-sheet-body { text-align: center; }
.info-sheet-mark {
  font-family: var(--font-gurmukhi);
  font-size: 56px; line-height: 1;
  color: var(--accent);
  margin-bottom: 6px;
}
.info-sheet-title {
  font-family: var(--font-display);
  font-size: 32px; font-weight: 500;
  color: var(--ink); margin: 0 0 8px;
}
.info-sheet-tagline {
  font-family: var(--font-display); font-style: italic;
  font-size: 15px; line-height: 1.5;
  color: var(--ink-3);
  margin: 0 0 24px;
}

.info-sheet-stats {
  display: flex; justify-content: center; gap: 24px;
  padding: 16px 0;
  border-top: 1px solid var(--hairline);
  border-bottom: 1px solid var(--hairline);
  margin-bottom: 22px;
}
.info-sheet-stat-value {
  font-family: var(--font-display); font-style: italic;
  font-size: 22px; font-weight: 500;
  color: var(--accent);
}
.info-sheet-stat-label {
  font-family: var(--font-mono); font-size: 9px;
  letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--ink-4); margin-top: 2px;
}

.info-sheet-links {
  display: flex; flex-direction: column; gap: 2px;
  margin-bottom: 20px;
}
.info-sheet-link {
  display: flex; align-items: center; justify-content: space-between;
  padding: 13px 14px;
  background: var(--surface);
  border: 1px solid var(--hairline);
  border-radius: 6px;
  text-decoration: none;
  color: var(--ink);
  transition: background 0.12s, border-color 0.12s;
}
.info-sheet-link:active {
  background: var(--surface-up);
  border-color: var(--rule);
}
.info-sheet-link-label {
  font-family: var(--font-display); font-style: italic;
  font-size: 16px; color: var(--ink);
}
.info-sheet-link svg { width: 16px; height: 16px; color: var(--ink-4); }

.info-sheet-disclaimer {
  font-family: var(--font-display); font-style: italic;
  font-size: 13px; line-height: 1.5;
  color: var(--ink-3);
  text-align: left;
  padding: 12px 14px;
  background: var(--surface);
  border-left: 3px solid var(--accent);
  border-radius: 0 4px 4px 0;
  margin-bottom: 18px;
}

.info-sheet-footer {
  font-family: var(--font-mono); font-size: 10px;
  letter-spacing: 0.1em; color: var(--ink-4);
  text-align: center;
}
.info-sheet-footer-dot { margin: 0 6px; color: var(--rule); }

@media (min-width: 540px) {
  #app { box-shadow: 0 0 60px rgba(28, 24, 20, 0.06); background: var(--paper); }
  body { background: #ebe3d2; }
}
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
"""

JS = r"""
(function () {
  'use strict';

  // ============ DATA ============
  const PAYLOAD = JSON.parse(document.getElementById('verse-data').textContent);
  const SOURCES = PAYLOAD.sources;
  const RAW = PAYLOAD.verses.map(v => ({
    a: v.a, l: v.l,
    s: SOURCES[v.s],
    g: v.g, r: v.r, e: v.e,
    id: v.a + '-' + v.l,
  }));

  const AVAILABLE_ANGS = [...new Set(RAW.map(v => v.a))].sort((a, b) => a - b);

  // ============ AnmolLipi -> Unicode Gurmukhi converter ============
  // Best-effort; handles the most common patterns. Edge cases will be
  // approximate. The aim is readable Gurmukhi, not perfect.
  const GUR = (function () {
    const cmap = {
      's':'ਸ','h':'ਹ','k':'ਕ','K':'ਖ','g':'ਗ','G':'ਘ','|':'ਙ',
      'c':'ਚ','C':'ਛ','j':'ਜ','J':'ਝ','\\':'ਞ',
      't':'ਟ','T':'ਠ','f':'ਡ','F':'ਢ','x':'ਣ',
      'q':'ਤ','Q':'ਥ','d':'ਦ','D':'ਧ','n':'ਨ',
      'p':'ਪ','P':'ਫ','b':'ਬ','B':'ਭ','m':'ਮ',
      'X':'ਯ','r':'ਰ','l':'ਲ','v':'ਵ','V':'ੜ',
      'S':'ਸ਼','L':'ਲ਼','z':'ਜ਼','Z':'ਗ਼','^':'ਖ਼',
    };
    const consonants = new Set(Object.keys(cmap));
    // Subjoined half-form glyphs (AnmolLipi). Most map to virama+consonant;
    // ü and ¨ are low-positioned vowel marks that follow subjoined letters.
    const subjoiners = {
      'H': '੍ਹ', '@': '੍ਹ',          // subjoined HAHA (two visual forms)
      'R': '੍ਰ', '®': '੍ਰ',          // subjoined RARA (two visual forms)
      '´': '੍ਯ',                     // subjoined YAYYA
      'Í': '੍ਵ',                     // subjoined VAVA
      'ç': '੍ਚ',                     // subjoined CHACHA
      '˜': '੍ਨ',                     // subjoined NANNA
      '†': '੍ਟ',                     // subjoined TAINKA (Sanskrit loans)
      'œ': '੍ਤ',                     // subjoined TATTA
      'ü': 'ੁ', '¨': 'ੂ',            // low-position aunkar / dulainkar
    };
    const matras = {
      'w':'ਾ','y':'ੇ','Y':'ੈ','o':'ੋ','O':'ੌ',
    };
    const numerals = ['੦','੧','੨','੩','੪','੫','੬','੭','੮','੯'];

    function convert(text) {
      if (!text) return '';
      let out = '';
      let i = 0;
      let lastWasConsonant = false;
      while (i < text.length) {
        const c = text[i];

        // <> -> Ek Onkar
        if (c === '<' && text[i + 1] === '>') {
          out += 'ੴ'; i += 2; lastWasConsonant = false; continue;
        }
        // ] -> dandi
        if (c === ']') {
          out += '॥'; i++; lastWasConsonant = false; continue;
        }
        // Numbers
        if (c >= '0' && c <= '9') {
          out += numerals[c.charCodeAt(0) - 48];
          i++; lastWasConsonant = false; continue;
        }
        // Space
        if (c === ' ') {
          out += ' '; i++; lastWasConsonant = false; continue;
        }

        // Trigraph ˆØI -> ੀਂ  (visual "bindi above bihari"; reorder to logical Unicode)
        if (c === 'ˆ' && text[i + 1] === 'Ø' && text[i + 2] === 'I') {
          out += 'ੀਂ'; i += 3; lastWasConsonant = false; continue;
        }

        // W -> ਾਂ  (kanna + bindi, e.g. ਜਾਂ, ਮਾਂ, ਭਾਂਡਾ)
        if (c === 'W') {
          out += 'ਾਂ'; i++; lastWasConsonant = false; continue;
        }

        // Pre-vowel sihari: 'i' + consonant. Consume any subjoined consonants
        // that follow so the sihari sits AFTER the full half-form cluster
        // (correct Unicode order: ਕ੍ਰਿ not ਕਿ੍ਰ).
        if (c === 'i' && i + 1 < text.length && consonants.has(text[i + 1])) {
          let cluster = cmap[text[i + 1]];
          let j = i + 2;
          while (j < text.length && subjoiners[text[j]] !== undefined
                 && subjoiners[text[j]].charCodeAt(0) === 0x0A4D) {
            cluster += subjoiners[text[j]];
            j++;
          }
          out += cluster + 'ਿ';
          i = j;
          lastWasConsonant = true;
          continue;
        }

        // Independent vowel digraphs. In AnmolLipi these encode the
        // standalone vowel forms (with carrier letter built in) and can
        // appear anywhere a syllable starts: word-initial, after a vowel
        // matra, OR after a consonant cluster (sihari). Previously these
        // only fired in !lastWasConsonant contexts, which missed every
        // mid-word occurrence like 'iDAwie' -> ਧਿਆਇ, 'kwieAw' -> ਕਾਇਆ.
        if (c === 'A' && text[i + 1] === 'w') {                      // ਆ
          out += 'ਆ'; i += 2; lastWasConsonant = false; continue;
        }
        if (c === 'A' && text[i + 1] === 'U') {                      // ਊ
          out += 'ਊ'; i += 2; lastWasConsonant = false; continue;
        }
        if (c === 'A' && text[i + 1] === 'Y') {                      // ਐ
          out += 'ਐ'; i += 2; lastWasConsonant = false; continue;
        }
        if (c === 'A' && text[i + 1] === 'O') {                      // ਔ
          out += 'ਔ'; i += 2; lastWasConsonant = false; continue;
        }
        if (c === 'a' && text[i + 1] === 'u') {                      // ਉ
          out += 'ਉ'; i += 2; lastWasConsonant = false; continue;
        }
        if (c === 'e' && text[i + 1] === 'I') {                      // ਈ
          out += 'ਈ'; i += 2; lastWasConsonant = false; continue;
        }
        if (c === 'e' && text[i + 1] === 'y') {                      // ਏ (rare digraph)
          out += 'ਏ'; i += 2; lastWasConsonant = false; continue;
        }
        if (c === 'i' && text[i + 1] === 'e') {                      // ਇ
          // Standard AnmolLipi encoding for independent ਇ. Note: this
          // only fires after the sihari rule above has already failed
          // (sihari needs 'i' + consonant; 'e' is not a consonant).
          out += 'ਇ'; i += 2; lastWasConsonant = false; continue;
        }
        if (c === 'a' && text[i + 1] === 'U') {                      // ਊ (lowercase variant of AU)
          out += 'ਊ'; i += 2; lastWasConsonant = false; continue;
        }

        // Independent vowel singles. These fire ANYWHERE — word-start, after
        // a vowel matra, or after a consonant cluster — because AnmolLipi
        // uses them as syllable-boundary independent vowels (e.g. 'ibAMq'
        // -> ਬਿਅੰਤ has an independent ਅ after the sihari ਬਿ; 'qirE' ->
        // ਤਰਿਏ has an independent ਏ after the sihari ਤਰਿ). Digraphs above
        // are tried first so 'Aw' beats lone 'A', etc.
        if (c === 'A') { out += 'ਅ'; i++; lastWasConsonant = false; continue; }
        if (c === 'E') { out += 'ਏ'; i++; lastWasConsonant = false; continue; }
        // Lowercase 'a' and 'e' only fire as independent vowels when NOT after
        // a consonant — otherwise they'd be mistaken for matras (which they
        // can't be, since 'a'/'e' aren't matra glyphs in AnmolLipi, but the
        // restriction is harmless and protects against spurious ਅ insertions).
        if (!lastWasConsonant) {
          if (c === 'a') { out += 'ਅ'; i++; lastWasConsonant = false; continue; }
          if (c === 'i') { out += 'ਇ'; i++; lastWasConsonant = false; continue; }
          if (c === 'I') { out += 'ਈ'; i++; lastWasConsonant = false; continue; }
          if (c === 'u') { out += 'ਉ'; i++; lastWasConsonant = false; continue; }
          if (c === 'U') { out += 'ਊ'; i++; lastWasConsonant = false; continue; }
          if (c === 'e') { out += 'ੲ'; i++; lastWasConsonant = false; continue; }
          if (c === 'O') { out += 'ਓ'; i++; lastWasConsonant = false; continue; }
        }
        // Rare: lone 'e' after consonant (e.g. 'geˆØI'). Treat as carrier ੲ.
        if (c === 'e') { out += 'ੲ'; i++; lastWasConsonant = false; continue; }

        // Matras after consonant (or after another matra)
        if (matras[c] !== undefined) {
          out += matras[c]; i++; lastWasConsonant = false; continue;
        }
        // Vowel-quality matras u/U/I as matras after a consonant
        if (c === 'u') { out += 'ੁ'; i++; lastWasConsonant = false; continue; }
        if (c === 'U') { out += 'ੂ'; i++; lastWasConsonant = false; continue; }
        if (c === 'I') { out += 'ੀ'; i++; lastWasConsonant = false; continue; }
        if (c === 'O') { out += 'ੌ'; i++; lastWasConsonant = false; continue; }

        // Subjoined half-forms and low-position vowel marks
        if (subjoiners[c] !== undefined) {
          out += subjoiners[c]; i++; lastWasConsonant = true; continue;
        }

        // Bindi / tippi / visarga (combine with previous letter)
        if (c === 'M') { out += 'ੰ'; i++; continue; }
        if (c === 'N') { out += 'ਂ'; i++; continue; }
        if (c === 'ˆ') { out += 'ਂ'; i++; continue; }   // bindi (alternate)
        if (c === '`') { out += 'ਃ'; i++; continue; }
        if (c === 'Ú') { out += 'ਃ'; i++; continue; }
        if (c === 'µ') { out += 'ਂ'; i++; continue; }
        if (c === 'Ø') { i++; continue; }              // font-positioning glyph; drop

        // Consonants
        if (cmap[c] !== undefined) {
          out += cmap[c]; i++; lastWasConsonant = true;
          continue;
        }

        // Pass-through for unknown
        out += c; i++;
      }
      return out;
    }

    // Cache to avoid re-converting the same lines
    const cache = new Map();
    function memoConvert(text) {
      if (cache.has(text)) return cache.get(text);
      const r = convert(text);
      if (cache.size < 5000) cache.set(text, r);
      return r;
    }
    return { convert: memoConvert };
  })();

  // ============ NORMALISATION ============
  const DIGRAPHS = [
    ['chh','c'],['shh','s'],
    ['kh','k'],['gh','g'],['ch','c'],['jh','j'],
    ['th','t'],['dh','d'],['ph','f'],['bh','b'],
    ['sh','s'],['zh','j'],
    ['aa','a'],['ee','i'],['ii','i'],
    ['oo','u'],['uu','u'],
    ['ai','e'],['ei','e'],['ay','e'],
    ['au','o'],['ou','o'],['aw','o'],
    ['w','v'],['y','i'],
  ];
  function normalize(text) {
    if (!text) return '';
    let t = text.toLowerCase().replace(/[-']/g, '').replace(/[^a-z\s]/g, ' ');
    for (const [a, b] of DIGRAPHS) t = t.split(a).join(b);
    return t.replace(/(.)\1+/g, '$1').replace(/\s+/g, ' ').trim();
  }
  const compact = s => s.replace(/\s+/g, '');

  // ============ INDEX ============
  const INDEX = RAW.map(v => ({
    ...v,
    rn: normalize(v.r),
    rc: compact(normalize(v.r)),
    en: v.e.toLowerCase(),
    enc: compact(v.e.toLowerCase()),
  }));
  const BY_ID = new Map();
  for (const v of INDEX) BY_ID.set(v.id, v);

  // Token -> verse-index map for fast pre-filter at scale.
  // Also store first-2-chars to allow approximate matching for misspellings.
  const TOKEN_INDEX_ROMAN = new Map();   // token -> Set of verse indices
  const PREFIX_INDEX_ROMAN = new Map();  // 3-char prefix -> Set of verse indices
  const TOKEN_INDEX_EN = new Map();
  for (let i = 0; i < INDEX.length; i++) {
    const v = INDEX[i];
    for (const tok of v.rn.split(' ')) {
      if (!tok) continue;
      if (!TOKEN_INDEX_ROMAN.has(tok)) TOKEN_INDEX_ROMAN.set(tok, []);
      TOKEN_INDEX_ROMAN.get(tok).push(i);
      const pre = tok.slice(0, 3);
      if (pre.length >= 2) {
        if (!PREFIX_INDEX_ROMAN.has(pre)) PREFIX_INDEX_ROMAN.set(pre, []);
        PREFIX_INDEX_ROMAN.get(pre).push(i);
      }
    }
    for (const tok of v.en.split(/\s+/)) {
      const t = tok.replace(/[^a-z]/g, '');
      if (!t) continue;
      if (!TOKEN_INDEX_EN.has(t)) TOKEN_INDEX_EN.set(t, []);
      TOKEN_INDEX_EN.get(t).push(i);
    }
  }

  // ============ SCORING ============
  function partialRatio(q, target) {
    if (!q || !target) return 0;
    if (target.includes(q)) return 100;
    if (q.length > target.length) return partialRatio(target, q);
    let best = 0;
    for (let i = 0; i <= target.length - q.length; i++) {
      let m = 0;
      for (let j = 0; j < q.length; j++) if (target[i + j] === q[j]) m++;
      const s = (m / q.length) * 100;
      if (s > best) best = s;
      if (best === 100) break;
    }
    return best;
  }

  /**
   * Improved ranking:
   *   Tier 1 (200+): exact phrase match (whole query as substring)
   *   Tier 2 (160+): all tokens present in order (consecutive)
   *   Tier 3 (120+): all tokens present in order (with gaps)
   *   Tier 4 (80+):  all tokens present (any order)
   *   Tier 5 (40+):  fuzzy partial / some tokens
   * Single-token queries skip phrase logic.
   */
  function scoreVerse(field, qNorm, qCompact, qTokens, v) {
    const target = field === 'roman' ? v.rn : v.en;
    const tcomp = field === 'roman' ? v.rc : v.enc;
    const tTokens = target.split(' ').filter(Boolean);

    // Tier 1: exact phrase as compact substring (covers all spellings)
    const partial = partialRatio(qCompact, tcomp);
    let score = 0.5 * partial;

    if (qTokens.length === 1) {
      // Single token — partial match is the whole story
      if (tTokens.includes(qTokens[0])) score += 60; // exact token match
      return score;
    }

    // Multi-token query
    const tTokenSet = new Set(tTokens);
    const matched = qTokens.filter(t => tTokenSet.has(t));

    // Tier 2: phrase as consecutive sequence
    const phrase = qTokens.join(' ');
    const targetWithBoundaries = ' ' + target + ' ';
    if (targetWithBoundaries.includes(' ' + phrase + ' ')) {
      score += 150; // big bonus: all tokens, in order, consecutive
      return score;
    }

    // Tier 3: all tokens in order with gaps
    if (matched.length === qTokens.length) {
      let inOrder = true; let lastIdx = -1;
      for (const t of qTokens) {
        const idx = tTokens.indexOf(t, lastIdx + 1);
        if (idx === -1) { inOrder = false; break; }
        lastIdx = idx;
      }
      if (inOrder) {
        score += 100;
        return score;
      }
    }

    // Tier 4: all tokens present (any order)
    if (matched.length === qTokens.length) {
      score += 60;
      return score;
    }

    // Tier 5: some tokens present, proportional + penalty
    const ratio = matched.length / qTokens.length;
    score += 40 * ratio;
    // Penalty for missing tokens
    score -= (1 - ratio) * 30;

    return score;
  }

  // Pre-filter candidates: indices that contain at least one query token or a
  // close prefix-variant. Avoids scoring all 60K verses on each query.
  function getCandidates(field, qTokens) {
    const candidateSet = new Set();
    const idx = field === 'roman' ? TOKEN_INDEX_ROMAN : TOKEN_INDEX_EN;
    for (const t of qTokens) {
      if (idx.has(t)) for (const i of idx.get(t)) candidateSet.add(i);
      if (field === 'roman' && t.length >= 3) {
        const pre = t.slice(0, 3);
        if (PREFIX_INDEX_ROMAN.has(pre)) {
          for (const i of PREFIX_INDEX_ROMAN.get(pre)) candidateSet.add(i);
        }
      }
    }
    return candidateSet;
  }

  function search(query, field, topK) {
    topK = topK || 50;
    const q = (query || '').trim();
    if (!q) return [];
    const qN = field === 'roman' ? normalize(q) : q.toLowerCase();
    const qC = compact(qN);
    if (!qC) return [];
    const qTokens = qN.split(' ').filter(Boolean);

    // Get candidates (small fraction of the full index)
    const candidates = getCandidates(field, qTokens);

    // If candidate set is empty (rare unknown query), fall back to full scan
    const indices = candidates.size > 0 ? [...candidates] : Array.from({length: INDEX.length}, (_, i) => i);

    const scored = [];
    for (const i of indices) {
      const v = INDEX[i];
      const s = scoreVerse(field, qN, qC, qTokens, v);
      if (s > 25) scored.push([s, v]);
    }
    scored.sort((a, b) => b[0] - a[0]);
    return scored.slice(0, topK);
  }

  function escapeHTML(s) {
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }
  function highlight(text, query) {
    const tokens = (query || '').toLowerCase().split(/\s+/).filter(t => t.length >= 2);
    let html = escapeHTML(text);
    for (const tok of tokens) {
      const re = new RegExp('(' + tok.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
      html = html.replace(re, '<mark>$1</mark>');
    }
    return html;
  }

  // ============ STATE ============
  const STORAGE = {
    BOOKMARKS: 'gurbanipath:bookmarks:v1',
    LAST_READ: 'gurbanipath:lastRead:v1',
    VOD_DATE:  'gurbanipath:vodDate:v1',
    VOD_ID:    'gurbanipath:vodId:v1',
    DISPLAY:   'gurbanipath:display:v1',
    READING_PLACE: 'gurbanipath:readingPlace:v1',
  };
  function getJSON(key, fallback) {
    try { const v = JSON.parse(localStorage.getItem(key) || 'null'); return v === null ? fallback : v; }
    catch { return fallback; }
  }
  function setJSON(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
  }

  let state = {
    activeTab: 'read',
    field: 'roman',
    query: '',
    currentVerse: null,
    currentAng: null,
    bookmarks: getJSON(STORAGE.BOOKMARKS, []),
    lastRead: getJSON(STORAGE.LAST_READ, []),
    display: getJSON(STORAGE.DISPLAY, { gurmukhi: true, roman: true, english: true, citation: true }),
    readingPlace: getJSON(STORAGE.READING_PLACE, null),
  };
  // Backfill any new display fields for users with prior settings
  if (state.display.citation === undefined) state.display.citation = true;

  function applyDisplayPrefs() {
    document.body.classList.toggle('hide-gurmukhi', !state.display.gurmukhi);
    document.body.classList.toggle('hide-roman',    !state.display.roman);
    document.body.classList.toggle('hide-english',  !state.display.english);
    document.body.classList.toggle('hide-citation', !state.display.citation);
  }
  applyDisplayPrefs();

  // ============ VERSE OF THE DAY ============
  function pickVerseOfDay() {
    const today = new Date().toDateString();
    const storedDate = localStorage.getItem(STORAGE.VOD_DATE);
    const storedId   = localStorage.getItem(STORAGE.VOD_ID);
    if (storedDate === today && storedId) {
      const v = BY_ID.get(storedId);
      if (v) return v;
    }
    const pool = INDEX.filter(v =>
      v.e.length > 40 && v.e.length < 200 && v.r.length > 30 && !/^\|\|/.test(v.e)
    );
    const chosen = pool[Math.floor(Math.random() * pool.length)] || INDEX[0];
    localStorage.setItem(STORAGE.VOD_DATE, today);
    localStorage.setItem(STORAGE.VOD_ID, chosen.id);
    return chosen;
  }

  function timeAgo(ts) {
    const sec = Math.floor((Date.now() - ts) / 1000);
    if (sec < 60) return 'just now';
    const min = Math.floor(sec / 60);
    if (min < 60) return min + ' minute' + (min === 1 ? '' : 's') + ' ago';
    const hr = Math.floor(min / 60);
    if (hr < 24) return hr + ' hour' + (hr === 1 ? '' : 's') + ' ago';
    const days = Math.floor(hr / 24);
    if (days < 7) return days + ' day' + (days === 1 ? '' : 's') + ' ago';
    const weeks = Math.floor(days / 7);
    if (weeks < 5) return weeks + ' week' + (weeks === 1 ? '' : 's') + ' ago';
    const months = Math.floor(days / 30);
    return months + ' month' + (months === 1 ? '' : 's') + ' ago';
  }

  function renderResumeCard() {
    const wrap = document.getElementById('resumeCard');
    if (!state.readingPlace) {
      wrap.innerHTML = '';
      wrap.style.display = 'none';
      return;
    }
    const v = BY_ID.get(state.readingPlace.vid);
    if (!v) {
      wrap.innerHTML = '';
      wrap.style.display = 'none';
      return;
    }
    wrap.style.display = 'block';
    const preview = v.r.length > 90 ? v.r.slice(0, 88) + '…' : v.r;
    wrap.innerHTML =
      '<div class="resume-eyebrow-row">' +
        '<span class="resume-eyebrow">' +
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 3h14v18l-7-5-7 5V3z"/></svg>' +
          'Continue Reading' +
        '</span>' +
        '<button class="resume-clear" id="resumeClear" aria-label="Clear">' +
          '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="14" height="14"><path d="M18 6L6 18M6 6l12 12"/></svg>' +
        '</button>' +
      '</div>' +
      '<p class="resume-preview">' + escapeHTML(preview) + '</p>' +
      '<div class="resume-meta">' +
        '<span class="resume-cite">Ang ' + v.a + ' · Line ' + v.l + ' · ' + escapeHTML(GUR.convert(v.s || '—')) + '</span>' +
        '<span class="resume-time">saved ' + timeAgo(state.readingPlace.ts) + '</span>' +
      '</div>';

    wrap.onclick = (e) => {
      if (e.target.closest('#resumeClear')) return;  // don't open when clearing
      openAng(v.a, v.id);
    };
    document.getElementById('resumeClear').onclick = (e) => {
      e.stopPropagation();
      state.readingPlace = null;
      setJSON(STORAGE.READING_PLACE, null);
      renderResumeCard();
      toast('Reading place cleared');
    };
  }

  function renderRead() {
    renderResumeCard();
    const vod = pickVerseOfDay();
    document.getElementById('vodGurmukhi').textContent = GUR.convert(vod.g);
    document.getElementById('vodRoman').textContent = vod.r;
    document.getElementById('vodEnglish').textContent = vod.e;
    document.getElementById('vodCitation').innerHTML =
      'Ang ' + vod.a + ' <span class="dot">·</span> Line ' + vod.l + ' <span class="dot">·</span> ' + escapeHTML(GUR.convert(vod.s || '—'));
    document.getElementById('vodCard').onclick = () => openAng(vod.a, vod.id);

    const cont = document.getElementById('continueList');
    if (state.lastRead.length === 0) {
      cont.innerHTML = '<div class="quick-item" style="opacity:0.55"><span class="label" style="font-size:14px;color:var(--ink-4)">Open any verse to begin a reading history</span></div>';
    } else {
      cont.innerHTML = state.lastRead.slice(0, 3).map(id => {
        const v = BY_ID.get(id);
        if (!v) return '';
        return '<button class="quick-item" data-vid="' + v.id + '">' +
          '<span class="label">' + escapeHTML(v.r.slice(0, 50)) + (v.r.length > 50 ? '…' : '') + '</span>' +
          '<span class="meta">Ang ' + v.a + '</span></button>';
      }).join('');
      cont.querySelectorAll('[data-vid]').forEach(btn => {
        btn.onclick = () => {
          const v = BY_ID.get(btn.dataset.vid);
          if (v) openAng(v.a, v.id);
        };
      });
    }

    const banis = [
      { name: 'Mool Mantar',     ang: 1,    meta: 'Japji Sahib · Pauri 1' },
      { name: 'Japji Sahib',     ang: 1,    meta: 'mÚ 1' },
      { name: 'So Dar (Rehras)', ang: 8,    meta: 'mÚ 1' },
      { name: 'Sohila',          ang: 12,   meta: 'mÚ 1' },
      { name: 'Sukhmani Sahib',  ang: 262,  meta: 'Gauri Sukhmani · mÚ 5' },
      { name: 'Asa di Var',      ang: 462,  meta: 'mÚ 1' },
      { name: 'Salok Sehskritee',ang: 1353, meta: 'mÚ 5' },
      { name: 'Mundavani',       ang: 1429, meta: 'mÚ 5' },
    ];
    const bl = document.getElementById('baniList');
    bl.innerHTML = banis.map(b =>
      '<button class="quick-item" data-ang="' + b.ang + '">' +
      '<span class="label">' + b.name + '</span>' +
      '<span class="meta">' + b.meta + '</span></button>'
    ).join('');
    bl.querySelectorAll('[data-ang]').forEach(btn => {
      btn.onclick = () => openAng(parseInt(btn.dataset.ang), null);
    });
  }

  function renderSearchResults() {
    const list = document.getElementById('searchResults');
    const status = document.getElementById('searchStatus');
    const left = document.getElementById('statusLeft');
    const right = document.getElementById('statusRight');

    if (!state.query.trim()) {
      status.style.display = 'none';
      list.innerHTML = '<li><div class="empty">' +
        '<div class="ornament">❋ ❋ ❋</div>' +
        '<div class="text">A word, a tukk you remember, or an idea — begin anywhere.</div>' +
        '</div></li>';
      return;
    }

    const t0 = performance.now();
    const hits = search(state.query, state.field);
    const ms = (performance.now() - t0).toFixed(0);

    status.style.display = 'flex';
    if (hits.length === 0) {
      left.textContent = '0 results';
      right.textContent = ms + ' ms';
      list.innerHTML = '<li><div class="empty">' +
        '<div class="ornament">❋</div>' +
        '<div class="text">No verses matched. Try a different spelling.</div>' +
        '</div></li>';
      return;
    }
    left.textContent = hits.length + ' result' + (hits.length === 1 ? '' : 's');
    right.textContent = ms + ' ms';

    list.innerHTML = hits.map((pair, i) => {
      const v = pair[1];
      const cite = 'Ang ' + v.a + ' · L' + v.l;
      const src  = GUR.convert(v.s || '—');
      const isBookmarked = state.bookmarks.includes(v.id);
      const gurmukhi = GUR.convert(v.g);
      const roman = highlight(v.r, state.query);
      const english = state.field === 'english' ? highlight(v.e, state.query) : escapeHTML(v.e);
      return '<li class="verse-card" data-vid="' + v.id + '" style="animation: viewfade 0.3s ease-out ' + (Math.min(i,8)*30) + 'ms backwards">' +
        '<div class="meta"><span class="cite">' + escapeHTML(cite) + '</span>' +
        '<span>' + escapeHTML(src) + (isBookmarked ? ' <span class="bookmark-mark">★</span>' : '') + '</span></div>' +
        '<p class="gurmukhi">' + escapeHTML(gurmukhi) + '</p>' +
        '<p class="roman">' + roman + '</p>' +
        '<p class="english">' + english + '</p>' +
        '</li>';
    }).join('');
    list.querySelectorAll('[data-vid]').forEach(card => {
      card.onclick = () => {
        const v = BY_ID.get(card.dataset.vid);
        if (v) openAng(v.a, v.id);
      };
    });
  }

  function renderSaved() {
    const list = document.getElementById('savedResults');
    if (state.bookmarks.length === 0) {
      list.innerHTML = '<li><div class="empty">' +
        '<div class="ornament">❋</div>' +
        '<div class="text">No saved verses yet. Long-press any verse to save it here.</div>' +
        '</div></li>';
      return;
    }
    list.innerHTML = state.bookmarks.map((id, i) => {
      const v = BY_ID.get(id);
      if (!v) return '';
      const cite = 'Ang ' + v.a + ' · L' + v.l;
      return '<li class="verse-card" data-vid="' + v.id + '" style="animation: viewfade 0.3s ease-out ' + (Math.min(i,8)*40) + 'ms backwards">' +
        '<div class="meta"><span class="cite">' + escapeHTML(cite) + '</span>' +
        '<span>' + escapeHTML(GUR.convert(v.s || '—')) + '</span></div>' +
        '<p class="gurmukhi">' + escapeHTML(GUR.convert(v.g)) + '</p>' +
        '<p class="roman">' + escapeHTML(v.r) + '</p>' +
        '<p class="english">' + escapeHTML(v.e) + '</p></li>';
    }).join('');
    list.querySelectorAll('[data-vid]').forEach(card => {
      card.onclick = () => {
        const v = BY_ID.get(card.dataset.vid);
        if (v) openAng(v.a, v.id);
      };
    });
  }

  // ============ ANG PAGE ============
  function openAng(angNum, highlightId) {
    const verses = INDEX.filter(v => v.a === angNum).sort((a, b) => a.l - b.l);
    if (verses.length === 0) {
      toast('Ang ' + angNum + ' not found');
      return;
    }
    const highlightVerse = highlightId ? verses.find(v => v.id === highlightId) : null;
    state.currentVerse = highlightVerse || verses[0];
    state.currentAng = angNum;

    if (highlightId && state.currentVerse) {
      state.lastRead = [state.currentVerse.id, ...state.lastRead.filter(id => id !== state.currentVerse.id)].slice(0, 10);
      setJSON(STORAGE.LAST_READ, state.lastRead);
    }

    document.getElementById('angTitle').textContent = 'Ang ' + angNum;
    const idx = AVAILABLE_ANGS.indexOf(angNum);
    document.getElementById('prevAng').disabled = (idx <= 0);
    document.getElementById('nextAng').disabled = (idx === -1 || idx >= AVAILABLE_ANGS.length - 1);

    const firstSrc = verses[0].s || '';
    const pageHeader =
      '<div class="ang-page-header">' +
      '<div class="ornament">❋</div>' +
      '<div class="label">Ang ' + angNum + '</div>' +
      '<div class="source">' + escapeHTML(GUR.convert(firstSrc)) + '</div>' +
      '</div>';

    const versesHTML = verses.map(v => {
      const isMatched = highlightVerse && v.id === highlightVerse.id;
      const isBookmarked = state.bookmarks.includes(v.id);
      return '<article class="verse-card' + (isMatched ? ' matched' : '') + '" data-vid="' + v.id + '">' +
        '<div class="meta">' +
        '<span class="cite">Line ' + v.l + '</span>' +
        '<span>' + escapeHTML(GUR.convert(v.s || '—')) + (isBookmarked ? ' <span class="bookmark-mark">★</span>' : '') + '</span>' +
        '</div>' +
        '<p class="gurmukhi">' + escapeHTML(GUR.convert(v.g)) + '</p>' +
        '<p class="roman">' + escapeHTML(v.r) + '</p>' +
        '<p class="english">' + escapeHTML(v.e) + '</p>' +
        '</article>';
    }).join('');

    const content = document.getElementById('overlayContent');
    content.innerHTML = pageHeader + '<div class="ang-page">' + versesHTML + '</div>';

    const overlay = document.getElementById('overlay');
    overlay.classList.add('open');
    overlay.setAttribute('aria-hidden', 'false');

    requestAnimationFrame(() => {
      content.scrollTop = 0;
      if (highlightVerse) {
        const el = content.querySelector('[data-vid="' + highlightVerse.id + '"]');
        if (el) {
          setTimeout(() => el.scrollIntoView({ behavior: 'smooth', block: 'center' }), 60);
        }
      }
    });
  }

  function closeOverlay() {
    document.getElementById('overlay').classList.remove('open');
    document.getElementById('overlay').setAttribute('aria-hidden', 'true');
    state.currentVerse = null;
    state.currentAng = null;
    if (state.activeTab === 'read') renderRead();
    if (state.activeTab === 'saved') renderSaved();
  }

  document.getElementById('prevAng').onclick = () => {
    if (state.currentAng == null) return;
    const i = AVAILABLE_ANGS.indexOf(state.currentAng);
    if (i > 0) openAng(AVAILABLE_ANGS[i - 1], null);
  };
  document.getElementById('nextAng').onclick = () => {
    if (state.currentAng == null) return;
    const i = AVAILABLE_ANGS.indexOf(state.currentAng);
    if (i >= 0 && i < AVAILABLE_ANGS.length - 1) openAng(AVAILABLE_ANGS[i + 1], null);
  };

  // Ang title -> jump-to-ang popover
  const angJump = document.getElementById('angJumpPopover');
  document.getElementById('angTitle').onclick = (e) => {
    e.stopPropagation();
    angJump.classList.toggle('open');
    if (angJump.classList.contains('open')) {
      const inp = document.getElementById('angJumpInput');
      inp.value = state.currentAng || '';
      setTimeout(() => inp.focus(), 50);
    }
  };
  document.getElementById('angJumpGo').onclick = () => {
    const v = parseInt(document.getElementById('angJumpInput').value);
    if (v >= 1 && v <= 1430) {
      angJump.classList.remove('open');
      openAng(v, null);
    } else {
      toast('Enter ang 1–1430');
    }
  };
  document.getElementById('angJumpInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') document.getElementById('angJumpGo').click();
  });
  document.addEventListener('click', e => {
    if (angJump.classList.contains('open') &&
        !angJump.contains(e.target) &&
        e.target.id !== 'angTitle') {
      angJump.classList.remove('open');
    }
  });

  // ============ ACTION SHEET ============
  let actionSheetVerse = null;
  let actionSheetMode = 'verse';  // 'verse' or 'display'

  function openActionSheet(v) {
    actionSheetMode = 'verse';
    actionSheetVerse = v;
    document.getElementById('asMode-verse').style.display = 'block';
    document.getElementById('asMode-display').style.display = 'none';
    document.getElementById('actionSheetCite').textContent =
      'Ang ' + v.a + ' · Line ' + v.l + ' · ' + GUR.convert(v.s || '—');
    document.getElementById('actionSheetText').textContent = v.r;
    const isBookmarked = state.bookmarks.includes(v.id);
    document.getElementById('actionBookmarkLabel').textContent =
      isBookmarked ? 'Remove bookmark' : 'Bookmark';
    const bmBtn = document.getElementById('actionBookmark');
    bmBtn.classList.toggle('active-state', isBookmarked);
    const path = bmBtn.querySelector('svg path');
    path.setAttribute('fill', isBookmarked ? 'currentColor' : 'none');

    // Reading place button label
    const isCurrentPlace = state.readingPlace && state.readingPlace.vid === v.id;
    document.getElementById('actionMarkPlaceLabel').textContent =
      isCurrentPlace ? 'Reading place set ✓' : 'Mark as reading place';
    const mpBtn = document.getElementById('actionMarkPlace');
    mpBtn.classList.toggle('active-state', isCurrentPlace);
    const mpPath = mpBtn.querySelector('svg path');
    mpPath.setAttribute('fill', isCurrentPlace ? 'currentColor' : 'none');

    const sheet = document.getElementById('actionSheet');
    sheet.hidden = false;
    requestAnimationFrame(() => sheet.classList.add('open'));
  }

  function openDisplayMenu() {
    actionSheetMode = 'display';
    actionSheetVerse = null;
    document.getElementById('asMode-verse').style.display = 'none';
    document.getElementById('asMode-display').style.display = 'block';
    // Set checkmarks
    document.getElementById('asDispGurmukhi').classList.toggle('active-state', state.display.gurmukhi);
    document.getElementById('asDispGurmukhi').querySelector('.check').textContent = state.display.gurmukhi ? '✓' : '';
    document.getElementById('asDispRoman').classList.toggle('active-state', state.display.roman);
    document.getElementById('asDispRoman').querySelector('.check').textContent = state.display.roman ? '✓' : '';
    document.getElementById('asDispEnglish').classList.toggle('active-state', state.display.english);
    document.getElementById('asDispEnglish').querySelector('.check').textContent = state.display.english ? '✓' : '';
    document.getElementById('asDispCitation').classList.toggle('active-state', state.display.citation);
    document.getElementById('asDispCitation').querySelector('.check').textContent = state.display.citation ? '✓' : '';

    const sheet = document.getElementById('actionSheet');
    sheet.hidden = false;
    requestAnimationFrame(() => sheet.classList.add('open'));
  }

  function closeActionSheet() {
    const sheet = document.getElementById('actionSheet');
    sheet.classList.remove('open');
    setTimeout(() => { sheet.hidden = true; actionSheetVerse = null; }, 300);
  }

  document.getElementById('actionBookmark').onclick = () => {
    if (!actionSheetVerse) return;
    const id = actionSheetVerse.id;
    const has = state.bookmarks.includes(id);
    if (has) {
      state.bookmarks = state.bookmarks.filter(x => x !== id);
      toast('Removed bookmark');
    } else {
      state.bookmarks = [id, ...state.bookmarks].slice(0, 200);
      toast('Saved');
    }
    setJSON(STORAGE.BOOKMARKS, state.bookmarks);
    if (state.currentAng != null) {
      const cur = state.currentVerse ? state.currentVerse.id : null;
      openAng(state.currentAng, cur);
    }
    closeActionSheet();
  };
  document.getElementById('actionMarkPlace').onclick = () => {
    if (!actionSheetVerse) return;
    const v = actionSheetVerse;
    const wasCurrent = state.readingPlace && state.readingPlace.vid === v.id;
    if (wasCurrent) {
      state.readingPlace = null;
      setJSON(STORAGE.READING_PLACE, null);
      toast('Reading place cleared');
    } else {
      state.readingPlace = { vid: v.id, ts: Date.now() };
      setJSON(STORAGE.READING_PLACE, state.readingPlace);
      toast('Reading place saved');
    }
    closeActionSheet();
  };
  document.getElementById('actionCopy').onclick = async () => {
    if (!actionSheetVerse) return;
    const v = actionSheetVerse;
    const text = GUR.convert(v.g) + '\n' + v.r + '\n' + v.e + '\n— Sri Guru Granth Sahib Ji, Ang ' + v.a + ', Line ' + v.l + ', ' + GUR.convert(v.s || '');
    try { await navigator.clipboard.writeText(text); toast('Copied'); }
    catch { toast('Could not copy'); }
    closeActionSheet();
  };
  document.getElementById('actionShare').onclick = async () => {
    if (!actionSheetVerse) return;
    const v = actionSheetVerse;
    const text = GUR.convert(v.g) + '\n' + v.r + '\n' + v.e + '\n— Sri Guru Granth Sahib Ji, Ang ' + v.a + ', Line ' + v.l + ', ' + GUR.convert(v.s || '');
    if (navigator.share) { try { await navigator.share({ text }); } catch {} }
    else { try { await navigator.clipboard.writeText(text); toast('Copied to share'); } catch { toast('Share not supported'); } }
    closeActionSheet();
  };
  // Display toggles
  function toggleDisplay(field) {
    state.display[field] = !state.display[field];
    setJSON(STORAGE.DISPLAY, state.display);
    applyDisplayPrefs();
    // Update the menu visually
    openDisplayMenu();
  }
  document.getElementById('asDispGurmukhi').onclick = () => toggleDisplay('gurmukhi');
  document.getElementById('asDispRoman').onclick    = () => toggleDisplay('roman');
  document.getElementById('asDispEnglish').onclick  = () => toggleDisplay('english');
  document.getElementById('asDispCitation').onclick = () => toggleDisplay('citation');

  document.getElementById('actionCancel').onclick = closeActionSheet;
  document.getElementById('actionSheetBackdrop').onclick = closeActionSheet;

  document.getElementById('moreBtn').onclick = () => {
    if (state.currentVerse) openActionSheet(state.currentVerse);
  };
  document.getElementById('displayBtn').onclick = () => openDisplayMenu();

  // ============ TOAST ============
  let toastTimer;
  function toast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove('show'), 1800);
  }

  // ============ TABS ============
  document.querySelectorAll('.bottom-tabs .tab').forEach(tab => {
    tab.onclick = () => {
      document.querySelectorAll('.bottom-tabs .tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
      tab.classList.add('active');
      const which = tab.dataset.tab;
      document.querySelector('.view[data-view="' + which + '"]').classList.add('active');
      state.activeTab = which;
      if (which === 'read') renderRead();
      if (which === 'search') {
        renderSearchResults();
        if (!state.query) document.getElementById('q').focus();
      }
      if (which === 'saved') renderSaved();
    };
  });

  // ============ SEARCH INPUT ============
  const $q = document.getElementById('q');
  const $clear = document.getElementById('searchClear');
  let searchTimer;
  $q.addEventListener('input', () => {
    state.query = $q.value;
    $clear.classList.toggle('visible', !!state.query);
    clearTimeout(searchTimer);
    searchTimer = setTimeout(renderSearchResults, 80);
  });
  $clear.onclick = () => {
    $q.value = ''; state.query = '';
    $clear.classList.remove('visible');
    renderSearchResults(); $q.focus();
  };
  document.querySelectorAll('#fieldToggle button').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('#fieldToggle button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      state.field = b.dataset.field;
      $q.placeholder = state.field === 'roman'
        ? 'haumai, har naam suhavi, naam japna…'
        : 'ego, the lord\'s name, contemplate…';
      renderSearchResults();
    };
  });
  document.querySelectorAll('.hint').forEach(h => {
    h.onclick = () => {
      $q.value = h.dataset.q; state.query = h.dataset.q;
      $clear.classList.add('visible');
      renderSearchResults();
    };
  });

  document.getElementById('overlayBack').onclick = closeOverlay;
  document.getElementById('aboutBtn').onclick = () => {
    document.getElementById('infoSheetVerseCount').textContent = RAW.length.toLocaleString();
    document.getElementById('infoSheetAngCount').textContent = AVAILABLE_ANGS.length.toLocaleString();
    const sheet = document.getElementById('infoSheet');
    sheet.hidden = false;
    requestAnimationFrame(() => sheet.classList.add('open'));
  };
  document.getElementById('infoSheetClose').onclick = closeInfoSheet;
  document.getElementById('infoSheetBackdrop').onclick = closeInfoSheet;
  function closeInfoSheet() {
    const sheet = document.getElementById('infoSheet');
    sheet.classList.remove('open');
    setTimeout(() => { sheet.hidden = true; }, 300);
  }
  document.addEventListener('keydown', e => {
    const overlay = document.getElementById('overlay');
    const sheet = document.getElementById('actionSheet');
    const infoSheet = document.getElementById('infoSheet');
    if (e.key === 'Escape') {
      if (!infoSheet.hidden) closeInfoSheet();
      else if (!sheet.hidden) closeActionSheet();
      else if (overlay.classList.contains('open')) closeOverlay();
    }
    if (overlay.classList.contains('open') && sheet.hidden && infoSheet.hidden) {
      if (e.key === 'ArrowLeft') document.getElementById('prevAng').click();
      if (e.key === 'ArrowRight') document.getElementById('nextAng').click();
    }
  });

  // Long-press for action sheet
  let pressTimer; let pressMoved = false; let pressStartXY = null;
  function onPressStart(e) {
    const card = e.target.closest('.verse-card[data-vid]');
    if (!card) return;
    pressMoved = false;
    const t = e.touches ? e.touches[0] : e;
    pressStartXY = { x: t.clientX, y: t.clientY };
    pressTimer = setTimeout(() => {
      const v = BY_ID.get(card.dataset.vid);
      if (v && !pressMoved) {
        if (navigator.vibrate) navigator.vibrate(8);
        openActionSheet(v);
      }
      pressTimer = null;
    }, 500);
  }
  function onPressMove(e) {
    if (!pressTimer || !pressStartXY) return;
    const t = e.touches ? e.touches[0] : e;
    if (Math.abs(t.clientX - pressStartXY.x) > 8 || Math.abs(t.clientY - pressStartXY.y) > 8) {
      pressMoved = true;
      clearTimeout(pressTimer); pressTimer = null;
    }
  }
  function onPressEnd() { if (pressTimer) { clearTimeout(pressTimer); pressTimer = null; } pressStartXY = null; }
  document.addEventListener('touchstart', onPressStart, { passive: true });
  document.addEventListener('touchmove',  onPressMove,  { passive: true });
  document.addEventListener('touchend',   onPressEnd,   { passive: true });
  document.addEventListener('touchcancel',onPressEnd,   { passive: true });
  document.addEventListener('mousedown',  onPressStart);
  document.addEventListener('mousemove',  onPressMove);
  document.addEventListener('mouseup',    onPressEnd);

  // ============ INIT ============
  renderRead();
  // Hide loader
  setTimeout(() => {
    const l = document.getElementById('loader');
    if (l) l.classList.add('hidden');
    setTimeout(() => l && l.remove(), 600);
  }, 100);

  // ============ SERVICE WORKER ============
  // Force-reload: nuke all caches and unregister SW. Used by both the
  // "Reload to latest" settings button and (after confirmation) by the
  // update banner. Reload always happens; if cache wipe fails, we still
  // reload — the browser will refetch from the server.
  async function forceReload() {
    try {
      const regs = await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map((r) => r.unregister()));
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
    } catch (err) {
      console.warn('Cache wipe failed (will reload anyway):', err);
    }
    location.reload();
  }
  window.__forceReload = forceReload;

  function showUpdateBanner() {
    const banner = document.getElementById('updateBanner');
    if (!banner) return;
    banner.classList.add('show');
  }
  function hideUpdateBanner() {
    const banner = document.getElementById('updateBanner');
    if (!banner) return;
    banner.classList.remove('show');
  }

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js', { scope: '/' })
        .catch((err) => console.warn('SW registration failed:', err));

      // Listen for messages from the SW. The activate handler posts
      // { type: 'SW_UPDATED' } when a new version takes over an existing
      // installation (not on first install). Show the banner so the
      // user can refresh on their own schedule.
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'SW_UPDATED') {
          showUpdateBanner();
        }
      });
    });

    // Wire up banner buttons (must be wired regardless of whether the
    // banner is currently visible — the user may dismiss and re-show).
    document.addEventListener('DOMContentLoaded', () => {
      const refreshBtn = document.getElementById('updateBannerRefresh');
      const dismissBtn = document.getElementById('updateBannerDismiss');
      if (refreshBtn) refreshBtn.addEventListener('click', forceReload);
      if (dismissBtn) dismissBtn.addEventListener('click', hideUpdateBanner);

      // Wire up the "Reload to latest" settings entry
      const reloadBtn = document.getElementById('asDispReload');
      if (reloadBtn) {
        reloadBtn.addEventListener('click', () => {
          if (confirm('Reload the app to fetch the latest version? Your bookmarks and reading place are preserved.')) {
            forceReload();
          }
        });
      }
    });
  }
})();
"""

BODY = r"""
<div class="loader" id="loader">
  <div class="ornament">❋</div>
  <div class="text">Preparing your reading space…</div>
</div>

<!-- Update-available banner: shown by SW message listener when a new SW
     activates over an existing install. Manually dismissible. -->
<div class="update-banner" id="updateBanner" role="status" aria-live="polite">
  <span>A new version is available</span>
  <button class="update-banner-refresh" id="updateBannerRefresh">Refresh</button>
  <button class="update-banner-dismiss" id="updateBannerDismiss" aria-label="Dismiss">×</button>
</div>

<div id="app">
  <header class="app-header">
    <div class="brand"><span class="punj">ੴ</span> <em>Gurbani Path</em></div>
    <button class="menu-icon" aria-label="About" id="aboutBtn">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M12 8v4M12 16h.01"/></svg>
    </button>
  </header>

  <main id="main">
    <section class="view active" data-view="read">
      <div class="resume-card" id="resumeCard" style="display:none;"></div>
      <article class="verse-of-day" id="vodCard">
        <div class="ornament">❋</div>
        <div class="label"><span class="eyebrow">Verse of the Moment</span></div>
        <p class="gurmukhi" id="vodGurmukhi">—</p>
        <p class="roman" id="vodRoman">—</p>
        <p class="english" id="vodEnglish">—</p>
        <div class="citation" id="vodCitation">—</div>
      </article>

      <h2 class="section-title">Recently Opened</h2>
      <div class="quick-list" id="continueList"></div>

      <h2 class="section-title">Begin a Bani</h2>
      <div class="quick-list" id="baniList"></div>
    </section>

    <section class="view" data-view="search">
      <div class="search-shell">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/>
        </svg>
        <input id="q" class="search-input" type="search"
          placeholder="haumai, har naam suhavi, naam japna…"
          autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" inputmode="search" />
        <button class="search-clear" id="searchClear" aria-label="Clear">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="14" height="14"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="field-toggle" id="fieldToggle">
        <button class="active" data-field="roman">Roman</button>
        <button data-field="english">English</button>
      </div>
      <div class="hints">
        <button class="hint" data-q="har naam suhavi">har naam suhavi</button>
        <button class="hint" data-q="haumai">haumai</button>
        <button class="hint" data-q="pavan guru paani pita">pavan guru paani pita</button>
        <button class="hint" data-q="ek onkar satgur prasad">ek onkar satgur prasad</button>
      </div>
      <div class="search-status" id="searchStatus" style="display:none;">
        <span id="statusLeft"></span><span id="statusRight"></span>
      </div>
      <ul class="verse-list" id="searchResults">
        <li><div class="empty">
          <div class="ornament">❋ ❋ ❋</div>
          <div class="text">A word, a tukk you remember, or an idea — begin anywhere.</div>
        </div></li>
      </ul>
    </section>

    <section class="view" data-view="saved">
      <h2 class="section-title">Bookmarks</h2>
      <ul class="verse-list" id="savedResults"></ul>
    </section>
  </main>

  <nav class="bottom-tabs">
    <button class="tab active" data-tab="read">
      <span class="tab-icon-bg">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M4 5a2 2 0 012-2h5v18H6a2 2 0 01-2-2V5zM13 3h5a2 2 0 012 2v14a2 2 0 01-2 2h-5V3z"/>
        </svg>
      </span>
      Read
    </button>
    <button class="tab" data-tab="search">
      <span class="tab-icon-bg">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.35-4.35"/>
        </svg>
      </span>
      Search
    </button>
    <button class="tab" data-tab="saved">
      <span class="tab-icon-bg">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M5 5v16l7-5 7 5V5a2 2 0 00-2-2H7a2 2 0 00-2 2z"/>
        </svg>
      </span>
      Saved
    </button>
  </nav>
</div>

<div class="overlay" id="overlay" aria-hidden="true">
  <header class="overlay-header">
    <button class="overlay-back" id="overlayBack">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M15 18l-6-6 6-6"/></svg>
      Back
    </button>
    <div class="ang-nav">
      <button class="ang-nav-btn" id="prevAng" aria-label="Previous ang">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M15 18l-6-6 6-6"/></svg>
      </button>
      <div class="ang-title" id="angTitle">Ang —</div>
      <button class="ang-nav-btn" id="nextAng" aria-label="Next ang">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M9 6l6 6-6 6"/></svg>
      </button>
    </div>
    <button class="overlay-icon-btn" id="displayBtn" aria-label="Display options">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M3 7h18M3 12h18M3 17h12"/>
      </svg>
    </button>
    <button class="overlay-icon-btn" id="moreBtn" aria-label="More">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="5" cy="12" r="1.4"/><circle cx="12" cy="12" r="1.4"/><circle cx="19" cy="12" r="1.4"/>
      </svg>
    </button>
  </header>
  <div class="overlay-content" id="overlayContent"></div>
  <div class="ang-jump-popover" id="angJumpPopover">
    <label>Jump to ang</label>
    <input type="number" id="angJumpInput" min="1" max="1430" inputmode="numeric" />
    <button id="angJumpGo">Go</button>
  </div>
</div>

<div class="action-sheet" id="actionSheet" hidden>
  <div class="action-sheet-backdrop" id="actionSheetBackdrop"></div>
  <div class="action-sheet-content">
    <div class="action-sheet-handle"></div>

    <div id="asMode-verse">
      <div class="action-sheet-preview">
        <span class="action-sheet-preview-cite" id="actionSheetCite"></span>
        <span id="actionSheetText"></span>
      </div>
      <button class="action-sheet-item" id="actionMarkPlace">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M5 3h14v18l-7-5-7 5V3z"/>
        </svg>
        <span id="actionMarkPlaceLabel">Mark as reading place</span>
      </button>
      <button class="action-sheet-item" id="actionBookmark">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M5 5v16l7-5 7 5V5a2 2 0 00-2-2H7a2 2 0 00-2 2z"/>
        </svg>
        <span id="actionBookmarkLabel">Bookmark</span>
      </button>
      <button class="action-sheet-item" id="actionCopy">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="8" y="8" width="13" height="13" rx="2"/>
          <path d="M16 8V5a2 2 0 00-2-2H5a2 2 0 00-2 2v9a2 2 0 002 2h3"/>
        </svg>
        Copy verse
      </button>
      <button class="action-sheet-item" id="actionShare">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M12 3v12M7 8l5-5 5 5M5 15v4a2 2 0 002 2h10a2 2 0 002-2v-4"/>
        </svg>
        Share verse
      </button>
    </div>

    <div id="asMode-display" style="display:none;">
      <div class="action-sheet-section">Show on each verse</div>
      <button class="action-sheet-item" id="asDispGurmukhi">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/></svg>
        Gurmukhi script
        <span class="check"></span>
      </button>
      <button class="action-sheet-item" id="asDispRoman">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 7h16M4 12h16M4 17h10"/></svg>
        Roman transliteration
        <span class="check"></span>
      </button>
      <button class="action-sheet-item" id="asDispEnglish">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M3 6l9 12 9-12"/></svg>
        English translation
        <span class="check"></span>
      </button>
      <button class="action-sheet-item" id="asDispCitation">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M4 4h16v4H4zM4 11h10M4 16h10M4 20h6"/>
        </svg>
        Line number &amp; source
        <span class="check"></span>
      </button>
      <div class="action-sheet-divider"></div>
      <button class="action-sheet-item" id="asDispReload">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M3 12a9 9 0 0 1 15.5-6.3L21 8M21 3v5h-5M21 12a9 9 0 0 1-15.5 6.3L3 16M3 21v-5h5"/>
        </svg>
        Reload to latest version
      </button>
      <div class="action-sheet-divider"></div>
    </div>

    <button class="action-sheet-item action-sheet-cancel" id="actionCancel">Cancel</button>
  </div>
</div>

<div class="toast" id="toast"></div>

<!-- INFO SHEET (About / site links) -->
<div class="info-sheet" id="infoSheet" hidden>
  <div class="info-sheet-backdrop" id="infoSheetBackdrop"></div>
  <div class="info-sheet-content">
    <button class="info-sheet-close" id="infoSheetClose" aria-label="Close">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M18 6L6 18M6 6l12 12"/></svg>
    </button>
    <div class="info-sheet-body">
      <div class="info-sheet-mark">ੴ</div>
      <h2 class="info-sheet-title"><em>Gurbani Path</em></h2>
      <p class="info-sheet-tagline">Search and read Sri Guru Granth Sahib Ji.<br/>Offered as seva to the worldwide sangat.</p>

      <div class="info-sheet-stats">
        <div class="info-sheet-stat">
          <div class="info-sheet-stat-value" id="infoSheetVerseCount">—</div>
          <div class="info-sheet-stat-label">Verses</div>
        </div>
        <div class="info-sheet-stat">
          <div class="info-sheet-stat-value" id="infoSheetAngCount">—</div>
          <div class="info-sheet-stat-label">Angs</div>
        </div>
        <div class="info-sheet-stat">
          <div class="info-sheet-stat-value">Free</div>
          <div class="info-sheet-stat-label">Forever</div>
        </div>
      </div>

      <div class="info-sheet-links">
        <a href="/about.html" class="info-sheet-link">
          <span class="info-sheet-link-label">About this project</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 6l6 6-6 6"/></svg>
        </a>
        <a href="/credits.html" class="info-sheet-link">
          <span class="info-sheet-link-label">Sources &amp; credits</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 6l6 6-6 6"/></svg>
        </a>
        <a href="/feedback.html" class="info-sheet-link">
          <span class="info-sheet-link-label">Send a correction or idea</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 6l6 6-6 6"/></svg>
        </a>
        <a href="/privacy.html" class="info-sheet-link">
          <span class="info-sheet-link-label">Privacy</span>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 6l6 6-6 6"/></svg>
        </a>
      </div>

      <div class="info-sheet-disclaimer">
        The Gurmukhi script is auto-converted from a legacy ASCII source and is approximate. The Roman transliteration and English translation are the canonical reference. Corrections gratefully welcomed.
      </div>

      <div class="info-sheet-footer">
        <a href="/" style="text-decoration: none; color: inherit;">gurbanipath.org</a>
        <span class="info-sheet-footer-dot">·</span>
        Code: AGPL-3.0
        <span class="info-sheet-footer-dot">·</span>
        Content: CC BY-SA 4.0
      </div>
    </div>
  </div>
</div>
"""

# Assemble the file
HEAD = (ROOT / 'build' / 'header_gp.html').read_text()
html = (
    HEAD
    + '<style>\n' + CSS + '\n</style>\n</head>\n<body>\n'
    + BODY
    + '\n<script id="verse-data" type="application/json">' + data_json + '</script>\n'
    + '<script>\n' + JS + '\n</script>\n'
    + '</body>\n</html>\n'
)

OUT.write_text(html, encoding='utf-8')
print(f"Wrote {OUT} ({OUT.stat().st_size / (1024 * 1024):.2f} MB)")
