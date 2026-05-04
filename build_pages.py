#!/usr/bin/env python3
"""Generate the static HTML pages (index, about, credits, privacy, feedback)
using a shared template so head/header/footer stay consistent.

Run: python3 build_pages.py
Output: public/*.html
"""
from pathlib import Path

OUT = Path('/home/claude/gurbanipath/public')

def head(title, description, path, full_title=None):
    """Return <head> block for a page. `path` is the canonical URL path."""
    canonical = f'https://gurbanipath.org{path}'
    title_text = full_title if full_title else f'{title} · Gurbani Path'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<meta name="theme-color" content="#f4eee2" />
<meta name="color-scheme" content="light" />
<title>{title_text}</title>
<meta name="description" content="{description}" />
<link rel="canonical" href="{canonical}" />

<!-- Open Graph / Twitter cards -->
<meta property="og:type" content="website" />
<meta property="og:url" content="{canonical}" />
<meta property="og:title" content="{title_text}" />
<meta property="og:description" content="{description}" />
<meta property="og:image" content="https://gurbanipath.org/icons/og-image.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:site_name" content="Gurbani Path" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{title_text}" />
<meta name="twitter:description" content="{description}" />
<meta name="twitter:image" content="https://gurbanipath.org/icons/og-image.png" />

<!-- Icons -->
<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="icon" type="image/png" sizes="32x32" href="/icons/icon-32.png" />
<link rel="icon" type="image/png" sizes="192x192" href="/icons/icon-192.png" />
<link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png" />
<link rel="manifest" href="/manifest.webmanifest" />

<!-- Fonts -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,500;0,8..60,600;1,8..60,400&family=Albert+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />

<link rel="stylesheet" href="/site.css" />

<style>
  /* Bundled Noto Serif Gurmukhi (offline-first) */
  @font-face {{
    font-family: 'Noto Serif Gurmukhi';
    font-style: normal;
    font-weight: 100 900;
    font-display: swap;
    src: url('/fonts/NotoSerifGurmukhi.ttf') format('truetype-variations'),
         url('/fonts/NotoSerifGurmukhi.ttf') format('truetype');
  }}
</style>
</head>
<body>
'''

def header(active=''):
    def cls(slug): return ' class="active"' if slug == active else ''
    return f'''<header class="site-header">
  <div class="site-header-inner">
    <a class="site-brand" href="/">
      <span class="ek-onkar">ੴ</span>
      <span><em>Gurbani Path</em></span>
    </a>
    <nav class="site-nav">
      <a href="/app/"{cls('app')}>Open App</a>
      <a href="/about.html"{cls('about')}>About</a>
      <a href="/credits.html"{cls('credits')}>Credits</a>
      <a href="/feedback.html"{cls('feedback')}>Feedback</a>
    </nav>
  </div>
</header>
'''

def footer():
    return '''<footer class="site-footer">
  <div class="site-footer-inner">
    <div class="footer-row">
      <a href="/about.html">About</a>
      <a href="/credits.html">Credits</a>
      <a href="/privacy.html">Privacy</a>
      <a href="/feedback.html">Feedback</a>
      <a href="https://github.com/gurbanipath/gurbanipath" target="_blank" rel="noopener">GitHub</a>
    </div>
    <div class="footer-row" style="font-family: var(--font-mono); font-size: 11px; letter-spacing: 0.1em; color: var(--ink-4); flex-direction: column; align-items: flex-start; gap: 4px;">
      <div>Code: AGPL-3.0 · Content: CC BY-SA 4.0</div>
      <div>A non-commercial seva project · gurbanipath.org</div>
    </div>
    <div class="footer-disclaimer">
      Offered as seva to the worldwide sangat. The text of Sri Guru Granth Sahib Ji is sacred; this app is a reading aid, not a replacement for the satikar of a physical Saroop or for traditional study.
    </div>
  </div>
</footer>
</body>
</html>
'''

def page(title, description, path, active, body, full_title=None):
    return head(title, description, path, full_title) + header(active) + '<main>\n' + body + '\n</main>\n' + footer()


# ============ INDEX (landing) ============

INDEX_BODY = '''
<section class="hero">
  <div class="ek-onkar-large">ੴ</div>
  <h1>Gurbani Path</h1>
  <p class="tagline">Search and read Sri Guru Granth Sahib Ji — calmly, openly, on any device.</p>
  <div class="btn-row" style="justify-content: center;">
    <a class="btn btn-primary" href="/app/">Open the App</a>
    <a class="btn btn-secondary" href="/about.html">About this project</a>
  </div>
</section>

<div class="ornament">❋ ❋ ❋</div>

<h2>What you can do</h2>

<div class="feature-grid">
  <div class="feature">
    <h4>Search the entire SGGS</h4>
    <p>Find any verse by typing a few words you remember in Roman or English. All 1,430 angs, instant results.</p>
  </div>
  <div class="feature">
    <h4>Read ang by ang</h4>
    <p>Tap any result to land on the full ang, with the matched verse highlighted and centered. Navigate prev/next, or jump to any ang.</p>
  </div>
  <div class="feature">
    <h4>See it your way</h4>
    <p>Toggle Gurmukhi script, Roman transliteration, and English translation independently. Read just one layer or all three.</p>
  </div>
  <div class="feature">
    <h4>Mark your reading place</h4>
    <p>Like a ribbon in a physical book — long-press any verse to save where you stopped, then resume from the home screen.</p>
  </div>
  <div class="feature">
    <h4>Bookmark verses you love</h4>
    <p>Collect verses for later study or sharing. Saved permanently on your device — no account, no sign-in.</p>
  </div>
  <div class="feature">
    <h4>Works offline</h4>
    <p>Once loaded, the entire corpus stays on your device. Read on a flight, in the gurdwara, anywhere.</p>
  </div>
</div>

<div class="disclaimer">
  <strong>An honest note:</strong> The Gurmukhi script in this app is auto-converted from a legacy ASCII source and is approximate. The Roman transliteration and English translation are the canonical reference layers. We are working to improve the Gurmukhi rendering. <a href="/about.html">Read more about sources and limitations.</a>
</div>

<h2>Add it to your phone</h2>

<p>Gurbani Path is a <strong>web app that becomes a phone app</strong> when you add it to your home screen. No App Store, no install — works on any modern phone.</p>

<dl>
  <dt>iPhone (Safari)</dt>
  <dd>Open <a href="/app/">gurbanipath.org/app</a> → tap the Share icon → <strong>Add to Home Screen</strong> → tap the new icon. Opens fullscreen, looks and feels like a real app.</dd>
  <dt>Android (Chrome)</dt>
  <dd>Open <a href="/app/">gurbanipath.org/app</a> → tap the menu (⋮) → <strong>Add to Home screen</strong> or <strong>Install app</strong>. Works the same way.</dd>
  <dt>Mac / Windows / Linux</dt>
  <dd>Just bookmark <a href="/app/">gurbanipath.org/app</a>. The app is responsive — same experience on any size screen.</dd>
</dl>

<div class="ornament">❋</div>

<h2>What this is, and what it isn't</h2>

<p>Gurbani Path is offered as <em>seva</em>. It is free, open-source, ad-free, tracker-free, and non-commercial. It will always be.</p>

<p>It is <strong>not</strong> a replacement for the satikar of a physical Saroop. It is not a substitute for traditional teaching, for sangat, for the physical practice of paath. It is a reading aid — a tool — to support those things.</p>

<p>It is <strong>not</strong> verified, pothi-grade text. The translations and transliterations are the work of others, gratefully bundled with their permission. The Gurmukhi rendering is approximate. <a href="/credits.html">Read who and what is behind the content.</a></p>

<p>It is <strong>not</strong> a competitor to the existing Sikh apps. It is one more tool in a healthy ecosystem of seva projects. <a href="/credits.html#prior-art">We learn from and acknowledge the work that came before.</a></p>

<div class="btn-row" style="justify-content: center; margin-top: 32px;">
  <a class="btn btn-primary" href="/app/">Open the App</a>
</div>
'''

(OUT / 'index.html').write_text(page(
    'Gurbani Path',
    'Search and read Sri Guru Granth Sahib Ji. A free, non-commercial reading and study aid offered as seva to the worldwide sangat.',
    '/', 'home', INDEX_BODY,
    full_title='Gurbani Path · Search and read Sri Guru Granth Sahib Ji'))


# ============ ABOUT ============

ABOUT_BODY = '''
<div class="eyebrow">About</div>
<h1>What this is</h1>

<p class="lede">A free, open-source reading and study aid for Sri Guru Granth Sahib Ji, offered with humility and reverence to the worldwide sangat.</p>

<h2>Why this exists</h2>

<p>The Sikh digital ecosystem already has wonderful tools — <a href="https://sikhitothemax.org" target="_blank" rel="noopener">SikhiToTheMax</a>, <a href="https://igurbani.com" target="_blank" rel="noopener">iGurbani</a>, <a href="https://banidb.com" target="_blank" rel="noopener">BaniDB</a>, and many others. We learned from all of them and use BaniDB-aligned sources where we can.</p>

<p>Gurbani Path adds something specific: a <strong>search-first</strong>, <strong>calm</strong>, <strong>typography-led</strong> reading experience that prioritises one thing — finding any verse you half-remember, quickly, on any device. No accounts, no ads, no gamification, no notifications begging for your attention. Just a quiet space to read.</p>

<h2>Design philosophy</h2>

<dl>
  <dt>Reverence over flash</dt>
  <dd>The visual language is borrowed from old Punjabi manuscripts — warm paper, silk-thread ornaments, restrained typography. No animations that distract from reading. No bright accents competing with the verses. The interface should disappear into the text.</dd>

  <dt>Search-first</dt>
  <dd>Most Sikhs already know SGGS verses by sound. They remember a tukk but not the ang. The fastest path from "I want this verse" to "I am reading it" is the central design problem we are solving.</dd>

  <dt>One layer or three, your call</dt>
  <dd>Gurmukhi readers want Gurmukhi. Diaspora Sikhs may want Roman + English. Scholars want all three side by side. The display options let each reader choose without negotiation.</dd>

  <dt>Privacy by absence</dt>
  <dd>We collect nothing. There is no analytics, no tracking, no account, no cloud sync. Your bookmarks and reading place live in your phone's browser storage and never leave it. <a href="/privacy.html">Read more.</a></dd>

  <dt>Offline-capable</dt>
  <dd>You should be able to open paath on a plane, in a basement, in any unreliable network. Once you visit once, the entire app and corpus are cached on your device.</dd>
</dl>

<h2>Sources and accuracy</h2>

<div class="disclaimer">
  <strong>Important:</strong> The Gurmukhi script displayed in this app is automatically converted from a legacy ASCII source to Unicode. The conversion is best-effort and will contain errors — particularly in compound clusters, rare diacritics, and edge cases. The Roman transliteration and English translation are the canonical reference layers; the Gurmukhi is a reading aid we are working to improve over time.
</div>

<p>The corpus we ship is built from these freely-available sources:</p>

<ul>
  <li><strong>English translation</strong> — Bhai Sant Singh Khalsa, MD (public domain)</li>
  <li><strong>Roman transliteration</strong> — Dr. Kulbir Singh Thind (freely shared)</li>
  <li><strong>Gurmukhi font</strong> — Noto Serif Gurmukhi (Google Fonts, SIL OFL)</li>
</ul>

<p>For the full credit list, including upstream digitizers, fonts, and tools used — see <a href="/credits.html">Credits</a>.</p>

<p>If you find an error, please <a href="/feedback.html">report it</a>. Verse corrections are the highest-priority issue type and we apply them as quickly as we can.</p>

<h2>What this isn't</h2>

<ul>
  <li><strong>Not a replacement for the physical Saroop.</strong> Read this app to support your study; do not let it replace the practice of going to the gurdwara, doing paath in front of the Saroop, or learning from teachers.</li>
  <li><strong>Not pothi-grade verified text.</strong> For authoritative reference, consult printed Saroops or scholarly sources. Use this for daily reading, search, and learning — not for citation in a research paper.</li>
  <li><strong>Not a commercial product.</strong> No advertising, no paid tier, no premium features. There is no business model. We accept no payment.</li>
  <li><strong>Not a competitor.</strong> SikhiToTheMax, iGurbani, Sundar Gutka, and others are excellent. Use what works for you. There is plenty of room.</li>
  <li><strong>Not affiliated</strong> with any Sikh institution, jathedar, or organisation. This is independent volunteer seva.</li>
</ul>

<h2>Roadmap</h2>

<p>This is Phase 1. Things we hope to add over time:</p>

<ul>
  <li>Verified, pothi-grade Unicode Gurmukhi (replacing the auto-conversion)</li>
  <li>Audio recitation aligned to verses</li>
  <li>Punjabi (Gurmukhi-script) translations and traditional teeka layers</li>
  <li>Native iOS and Android apps (currently a Progressive Web App)</li>
  <li>Daily Hukamnama from Sri Harmandir Sahib</li>
  <li>Reading streaks and progress tracking — <em>only if</em> we can do it without gamifying the act of reading Bani</li>
</ul>

<p>Some things we will <strong>not</strong> add: in-app purchases, social features that pressure people to share their reading, push notifications nagging users, advertising, third-party tracking.</p>

<h2>Contributing</h2>

<p>Gurbani Path is open source. The code lives on GitHub. Pull requests are welcome — particularly for:</p>

<ul>
  <li>Verse corrections (the most valuable kind of contribution)</li>
  <li>Improvements to the Gurmukhi auto-conversion</li>
  <li>Translation polish</li>
  <li>Accessibility fixes</li>
  <li>Bug reports and reproduction cases</li>
</ul>

<p>See the <a href="https://github.com/gurbanipath/gurbanipath/blob/main/README.md" target="_blank" rel="noopener">README</a> for technical details and contributing guidelines.</p>

<div class="ornament">❋</div>

<p style="text-align: center; font-family: var(--font-display); font-style: italic; font-size: 18px; color: var(--ink-3); margin-top: 24px;">ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖਾਲਸਾ, ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫ਼ਤਹਿ ॥</p>
'''

(OUT / 'about.html').write_text(page(
    'About',
    'About Gurbani Path — a free, non-commercial reading and study aid for Sri Guru Granth Sahib Ji.',
    '/about.html', 'about', ABOUT_BODY))


# ============ CREDITS ============

CREDITS_BODY = '''
<div class="eyebrow">Credits</div>
<h1>Sources and contributors</h1>

<p class="lede">Gurbani Path stands on the seva and scholarship of others. Every source, every contributor, gratefully acknowledged.</p>

<h2>The eternal source</h2>

<div class="card accent">
  <p style="margin: 0; font-family: var(--font-display); font-style: italic; font-size: 20px; color: var(--ink);"><strong style="font-style: normal; font-family: var(--font-body);">Sri Guru Granth Sahib Ji</strong> — the eternal Guru of the Sikhs, whose Word this project exists to make more accessible.</p>
</div>

<h2>Translations and transliterations</h2>

<dl>
  <dt>English translation</dt>
  <dd>
    <strong>Bhai Sant Singh Khalsa, MD</strong>. His complete English translation of Sri Guru Granth Sahib Ji has been freely circulated for decades and is widely used across the Sikh digital ecosystem. The translation is in the public domain. We are deeply grateful for his decades of seva.
  </dd>

  <dt>Roman transliteration</dt>
  <dd>
    <strong>Dr. Kulbir Singh Thind</strong>. His Roman transliteration of the entire SGGS is the foundational digital resource that nearly every Sikh app and website has been built on for the past 30+ years. He has freely shared this work without restriction, asking only that it be used in service of the panth. We use it with profound gratitude.
  </dd>

  <dt>Source compilation</dt>
  <dd>
    The compiled source from which our text was extracted is widely distributed as <em>"Sri Guru Granth Sahib Ji Darpan English"</em>. The original compilers and digitizers of this resource are unknown to us; if you know them, <a href="/feedback.html">please tell us</a> so we may credit them properly.
  </dd>
</dl>

<h2>Fonts</h2>

<dl>
  <dt>Noto Serif Gurmukhi · Noto Sans Gurmukhi</dt>
  <dd>
    <a href="https://fonts.google.com/specimen/Noto+Serif+Gurmukhi" target="_blank" rel="noopener">Google Fonts / Google Inc.</a> Licensed under the SIL Open Font License v1.1. Bundled in this site for offline-first use.
  </dd>

  <dt>Cormorant Garamond, Source Serif 4, Albert Sans, JetBrains Mono</dt>
  <dd>
    Used in the website and app interface. All open-licensed via Google Fonts under SIL OFL or similar permissive licenses.
  </dd>
</dl>

<h2 id="prior-art">Inspiration and prior art</h2>

<p>We are grateful to the existing Sikh digital ecosystem that paved the way and from which we have learned:</p>

<ul>
  <li><strong><a href="https://banidb.com" target="_blank" rel="noopener">BaniDB</a></strong> — the most thorough open SGGS database project, maintained by the Khalis Foundation. Future versions of Gurbani Path may consume BaniDB upstream rather than re-deriving text.</li>
  <li><strong><a href="https://sikhitothemax.org" target="_blank" rel="noopener">SikhiToTheMax</a></strong> — the most widely-used Gurbani presentation app; it set many UX expectations the panth has come to rely on.</li>
  <li><strong><a href="https://igurbani.com" target="_blank" rel="noopener">iGurbani</a></strong> — beautiful mobile reading experience; influenced this project's typography.</li>
  <li><strong>Khalis Foundation, Sikhnet, Sundar Gutka, and the broader Sikh open-source community.</strong></li>
</ul>

<p>This project is not a competitor to any of the above — there is room for many tools, each with different strengths and approaches.</p>

<h2>Maintainers</h2>

<p>Gurbani Path is maintained by the <strong>Gurbani Path Sevadars</strong>, a volunteer collective. The current maintainer list lives in <a href="https://github.com/gurbanipath/gurbanipath/blob/main/CONTRIBUTORS.md" target="_blank" rel="noopener">CONTRIBUTORS.md</a> on GitHub.</p>

<p>If you have contributed code, content, corrections, design feedback, or any other form of seva to this project, please add yourself to that file in a pull request. Every contribution counts.</p>

<h2>Tools and infrastructure</h2>

<ul>
  <li><strong>Hosting:</strong> <a href="https://pages.cloudflare.com" target="_blank" rel="noopener">Cloudflare Pages</a> (free tier)</li>
  <li><strong>Source control:</strong> <a href="https://github.com" target="_blank" rel="noopener">GitHub</a></li>
  <li><strong>Domain:</strong> <a href="https://gurbanipath.org">gurbanipath.org</a></li>
</ul>

<h2>Development assistance</h2>

<p>The code, design, and copy of this project were developed with substantial assistance from <strong>Claude</strong> (an AI assistant by <a href="https://anthropic.com" target="_blank" rel="noopener">Anthropic</a>) used as a coding and design collaborator. All editorial decisions, content sourcing decisions, final review, and acceptance of the work were made by human sevadars. We acknowledge this transparently because honesty about how the project was built matters as much as the work itself.</p>

<h2>Reporting omissions</h2>

<p>If we have failed to credit you or your work, please <a href="/feedback.html">let us know</a>. We will correct the credit promptly and publicly.</p>

<div class="ornament">❋</div>

<p style="text-align: center; font-family: var(--font-display); font-style: italic; font-size: 18px; color: var(--ink-3); margin-top: 24px;">ਧੰਨਵਾਦ।</p>
'''

(OUT / 'credits.html').write_text(page(
    'Credits',
    'Sources, contributors, and acknowledgments for the Gurbani Path project.',
    '/credits.html', 'credits', CREDITS_BODY))


# ============ PRIVACY ============

PRIVACY_BODY = '''
<div class="eyebrow">Privacy</div>
<h1>What we collect (nothing)</h1>

<p class="lede">Gurbani Path is built so there is nothing to collect. This page exists to confirm what we don't do, and to be transparent about the few things we do.</p>

<h2>What we do not collect</h2>

<ul>
  <li>We do <strong>not</strong> use Google Analytics, Cloudflare Analytics, or any other analytics service.</li>
  <li>We do <strong>not</strong> place any tracking cookies.</li>
  <li>We do <strong>not</strong> have user accounts. There is nothing to sign up for.</li>
  <li>We do <strong>not</strong> show advertisements.</li>
  <li>We do <strong>not</strong> share, sell, or transmit any information about you to anyone.</li>
  <li>We do <strong>not</strong> have a server that stores user data, because there is no user data.</li>
</ul>

<h2>What stays on your device</h2>

<p>The app saves a small amount of data <strong>in your browser, on your device only</strong>. This data never leaves your device and we cannot see it:</p>

<dl>
  <dt>Bookmarks</dt>
  <dd>Verses you save to your collection are stored in your browser's local storage. They persist between visits but are tied to your specific browser.</dd>

  <dt>Reading place</dt>
  <dd>The current ang and verse you marked to resume from. Same — local to your browser.</dd>

  <dt>Display preferences</dt>
  <dd>Whether you have Gurmukhi/Roman/English/citation visible — local to your browser.</dd>

  <dt>Verse of the Moment</dt>
  <dd>The randomly chosen daily verse, plus the date it was chosen. Local.</dd>
</dl>

<p>You can clear all of this at any time by clearing your browser's site data for gurbanipath.org. Doing so will remove your bookmarks and reading place — there is no cloud backup, because we do not have a cloud.</p>

<h2>What our hosting provider sees</h2>

<p>The site is hosted on <a href="https://pages.cloudflare.com" target="_blank" rel="noopener">Cloudflare Pages</a>. Cloudflare's infrastructure necessarily processes the HTTP request to deliver the page to you — that includes your IP address, your browser's user-agent string, and which page you requested. This is true of any website on the internet.</p>

<p>We have <strong>not</strong> enabled Cloudflare Web Analytics for Gurbani Path. Cloudflare's standard request logs are retained briefly per their <a href="https://www.cloudflare.com/privacypolicy/" target="_blank" rel="noopener">privacy policy</a>; we do not access these logs.</p>

<h2>What about fonts from Google?</h2>

<p>Some pages reference fonts hosted on Google Fonts (Cormorant Garamond, Source Serif, etc.). When you load a page, your browser fetches these from <code>fonts.googleapis.com</code>. Google's privacy policy applies to that interaction.</p>

<p>The Gurmukhi font (Noto Serif Gurmukhi) is <strong>bundled with this site</strong> and served from gurbanipath.org directly — no external fetch.</p>

<p>We may bundle the other fonts in a future update to remove all third-party requests. <a href="https://github.com/gurbanipath/gurbanipath/issues" target="_blank" rel="noopener">Track this on GitHub</a>.</p>

<h2>If you contact us</h2>

<p>If you email <strong>feedback@gurbanipath.org</strong> or open a GitHub Issue, we will see your message and your email/GitHub username. We will not share these with anyone or use them for anything beyond responding to you.</p>

<p>If you ask us to delete a message you sent us, we will.</p>

<h2>Changes to this notice</h2>

<p>If anything about how we handle data changes — for instance, if we add an opt-in privacy-respecting analytics tool — we will update this page and note the change in our <a href="https://github.com/gurbanipath/gurbanipath/commits/main/public/privacy.html" target="_blank" rel="noopener">commit history</a>. We will not silently change anything.</p>

<h2>Contact</h2>

<p>Questions about privacy: <a href="/feedback.html">Feedback page</a>, or email <strong>feedback@gurbanipath.org</strong>.</p>

<hr />

<p style="font-family: var(--font-mono); font-size: 12px; color: var(--ink-4); letter-spacing: 0.06em;">Last updated: this page is dated by its commit history on GitHub. Check <a href="https://github.com/gurbanipath/gurbanipath/commits/main/public/privacy.html" target="_blank" rel="noopener">the commit log</a> for the most recent change.</p>
'''

(OUT / 'privacy.html').write_text(page(
    'Privacy',
    'Gurbani Path collects nothing. No tracking, no analytics, no user accounts. This page explains exactly what data does and does not exist.',
    '/privacy.html', 'privacy', PRIVACY_BODY))


# ============ FEEDBACK ============

FEEDBACK_BODY = '''
<div class="eyebrow">Feedback</div>
<h1>Send us corrections and ideas</h1>

<p class="lede">Your eyes catch things we miss. Verse corrections, bug reports, and thoughtful suggestions are how this project gets better.</p>

<h2>Three ways to reach us</h2>

<div class="feature-grid">
  <div class="feature">
    <h4>GitHub Issues (preferred)</h4>
    <p>Tracked, public, version-controlled. Best for verse corrections and reproducible bugs. Anyone can browse and follow along.</p>
    <p style="margin-top: 12px;"><a class="btn btn-primary" href="https://github.com/gurbanipath/gurbanipath/issues/new/choose" target="_blank" rel="noopener" style="font-size: 12px; padding: 10px 16px;">Open an Issue</a></p>
  </div>
  <div class="feature">
    <h4>Email</h4>
    <p>For corrections that include lengthy attachments, sensitive matters, or anything that doesn't fit a public issue.</p>
    <p style="margin-top: 12px;"><a class="btn btn-secondary" href="mailto:feedback@gurbanipath.org" style="font-size: 12px; padding: 10px 16px;">feedback@gurbanipath.org</a></p>
  </div>
</div>

<div class="card">
  <h4 style="margin-top: 0;">Volunteer your time</h4>
  <p style="font-family: var(--font-body); font-style: normal; font-size: 16px; color: var(--ink-2); margin-bottom: 0;">Are you a Punjabi speaker who can review Gurmukhi conversion errors? A Gurmukhi typesetter who can help correct character mappings? A teacher who can suggest study features? A designer who can improve the typography? <a href="mailto:feedback@gurbanipath.org">Get in touch.</a> Most useful seva will be reviewing the auto-converted Gurmukhi against the original printed Saroop.</p>
</div>

<h2>What's most helpful to report</h2>

<dl>
  <dt>Verse corrections (highest priority)</dt>
  <dd>If a Gurmukhi line, transliteration, or translation is wrong, please tell us — with the ang and line numbers. Use the <a href="https://github.com/gurbanipath/gurbanipath/issues/new?template=correction.md" target="_blank" rel="noopener">verse correction template</a> on GitHub for the cleanest format.</dd>

  <dt>Bugs you can reproduce</dt>
  <dd>What you tried to do, what happened instead, and what device/browser you were using. <a href="https://github.com/gurbanipath/gurbanipath/issues/new?template=bug.md" target="_blank" rel="noopener">Bug template.</a></dd>

  <dt>Suggestions, with context</dt>
  <dd>"This would be nice" is fine but "This would help me when I'm doing nitnem because…" is better. Tell us who benefits and what problem it solves. <a href="https://github.com/gurbanipath/gurbanipath/issues/new?template=suggestion.md" target="_blank" rel="noopener">Suggestion template.</a></dd>

  <dt>Missing credits</dt>
  <dd>If your work, or someone else's, is bundled here without being properly credited — please <a href="mailto:feedback@gurbanipath.org">tell us at once</a>. We will fix the credit publicly.</dd>
</dl>

<h2>What we ask for in return</h2>

<ul>
  <li><strong>Patience.</strong> This is volunteer seva. We will respond as we can.</li>
  <li><strong>Specificity.</strong> "It's broken on my phone" is hard to fix; "It crashes when I tap the third bookmark on iPhone 13 Safari" is fixable.</li>
  <li><strong>Charity.</strong> Assume good faith. We assume the same of you.</li>
  <li><strong>Reading our <a href="/about.html">About page</a></strong> before suggesting features — some intentional design choices (no audio yet, no accounts, no gamification) are <em>features</em>, not gaps.</li>
</ul>

<div class="ornament">❋</div>

<p style="text-align: center; font-family: var(--font-display); font-style: italic; font-size: 18px; color: var(--ink-3); margin-top: 24px;">ਧੰਨਵਾਦ।</p>
'''

(OUT / 'feedback.html').write_text(page(
    'Feedback',
    'How to send corrections, bug reports, and suggestions for Gurbani Path.',
    '/feedback.html', 'feedback', FEEDBACK_BODY))


# ============ NOT-FOUND (404) ============

NOTFOUND_BODY = '''
<section class="hero">
  <div class="ek-onkar-large">❋</div>
  <h1>Not found</h1>
  <p class="tagline">The page you were looking for does not exist on this site.</p>
  <div class="btn-row" style="justify-content: center;">
    <a class="btn btn-primary" href="/">Return home</a>
    <a class="btn btn-secondary" href="/app/">Open the app</a>
  </div>
</section>
'''

(OUT / '404.html').write_text(page(
    'Not found',
    'The page you were looking for does not exist on this site.',
    '/404.html', '', NOTFOUND_BODY))


print("Generated:")
for f in sorted(OUT.glob('*.html')):
    size_kb = f.stat().st_size / 1024
    print(f"  {f.name:20s}  {size_kb:6.1f} KB")
