# Deployment Guide

This document walks you through getting `gurbanipath.org` live on the open
web, from a zip of source files to a working website. Estimated time: **45
minutes** the first time, including waits.

---

## Prerequisites

- The `gurbanipath` source files (this repository)
- A **GitHub account** (free) — sign up at https://github.com if needed
- A **Cloudflare account** (free) — sign up at https://cloudflare.com
- Control of the domain `gurbanipath.org` at your domain registrar
  (whoever you bought it from — GoDaddy, Namecheap, Google Domains, etc.)

---

## Step 1 — Push the source to GitHub (10 minutes)

1. Go to https://github.com/new
2. **Repository name:** `gurbanipath`
3. **Description:** `Search and read Sri Guru Granth Sahib Ji — gurbanipath.org`
4. **Public** (this is open-source seva)
5. **Do NOT** check "Add a README" — we already have one
6. Click **Create repository**

GitHub now shows you setup instructions. Use the **"…or push an existing
repository from the command line"** block. From your local copy of this
project:

```bash
cd path/to/gurbanipath
git init
git add .
git commit -m "Initial commit — Phase 1"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/gurbanipath.git
git push -u origin main
```

If GitHub asks for a password during `git push`, it actually wants a
**Personal Access Token** (PAT). Create one at
https://github.com/settings/tokens → "Fine-grained tokens" → with
permissions for the `gurbanipath` repo. Use that token in place of
the password.

After push, refresh GitHub. You should see all your files on the repo
page.

---

## Step 2 — Connect Cloudflare Pages to the GitHub repo (15 minutes)

1. Sign in to https://dash.cloudflare.com
2. In the left sidebar, click **Workers & Pages**
3. Click **Create application** → **Pages** tab → **Connect to Git**
4. Click **Connect GitHub** and authorize Cloudflare to read your
   repos. You can grant access to *only* the `gurbanipath` repo if you
   prefer.
5. Select the `gurbanipath` repository.
6. **Set up builds and deployments** — fill in:
   - **Project name:** `gurbanipath` (this is just a Cloudflare
     internal label)
   - **Production branch:** `main`
   - **Framework preset:** *None*
   - **Build command:** *(leave blank — there's no build step)*
   - **Build output directory:** `public`
   - **Root directory (advanced):** *(leave blank)*
   - **Environment variables:** *(none needed)*
7. Click **Save and Deploy**

Cloudflare will deploy. After ~30 seconds you'll see a URL like:
`https://gurbanipath.pages.dev` — that's your site already live, on a
Cloudflare-provided subdomain.

**Test it:** open that URL. You should see the landing page. The app
should work at `/app/`. If something is broken, fix it locally, commit,
push — Cloudflare auto-deploys.

---

## Step 3 — Connect your custom domain (15 minutes + DNS wait)

1. In Cloudflare Pages, open your `gurbanipath` project
2. Go to **Custom domains** tab → **Set up a custom domain**
3. Enter `gurbanipath.org` → **Continue**
4. Cloudflare will ask whether to proxy through Cloudflare (recommended:
   yes — gives you DDoS protection, free CDN, free SSL)

You now have **two paths** depending on where your domain is registered:

### Path A — Move DNS to Cloudflare (recommended, free, faster)

This is what Cloudflare prefers and what gives you the best performance.

1. Cloudflare will give you **two nameservers** like:
   `xyz.ns.cloudflare.com` and `abc.ns.cloudflare.com`
2. Log into your domain registrar (GoDaddy / Namecheap / Google
   Domains / wherever you bought `gurbanipath.org`)
3. Find the **DNS / Nameservers** setting for `gurbanipath.org`
4. Replace the existing nameservers with the two Cloudflare ones
5. Save

DNS propagation takes anywhere from **a few minutes to 24 hours**;
usually under an hour. While waiting, you can continue using the
`pages.dev` URL.

### Path B — Add CNAME records (works without moving nameservers)

If you don't want to move nameservers:

1. In your registrar's DNS settings, add these records:
   - **Type:** CNAME · **Name:** `@` · **Value:** `gurbanipath.pages.dev`
   - **Type:** CNAME · **Name:** `www` · **Value:** `gurbanipath.pages.dev`
2. *(Some registrars don't allow CNAME at root; in that case use Path A.)*

---

## Step 4 — Verify HTTPS and final checks (5 minutes)

Once DNS has propagated:

1. Visit `https://gurbanipath.org` — should load the landing page with
   a valid SSL lock icon
2. Visit `https://gurbanipath.org/app/` — should load the app
3. Try search: type `har naam suhavi` → first result should be Ang 726
4. On phone: open in Safari, Share → Add to Home Screen → tap the
   icon. Should open as a fullscreen app
5. Toggle airplane mode and reopen the home-screen icon — should still
   work (service worker cache)

If HTTPS doesn't work after 30 minutes, check Cloudflare Pages →
Custom domains; you may need to click "Verify domain" there.

---

## Step 5 — (Optional) Apply for Project Galileo

Cloudflare's [Project Galileo](https://www.cloudflare.com/galileo/) gives
qualifying non-profits and civil-society organizations free advanced
DDoS protection at no cost. Religious community resources qualify.

1. Visit https://www.cloudflare.com/galileo/
2. Click **Apply Now**
3. Fill the form — describe Gurbani Path as a non-commercial seva
   project for the worldwide Sikh sangat
4. Wait for review (1–4 weeks usually)

Not required, but recommended once you have any meaningful traffic.

---

## Updating the site

See `_docs/UPDATING.md`.

## DNS reference

If something breaks, see `_docs/DNS.md` for the exact records.
