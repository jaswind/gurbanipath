#!/usr/bin/env python3
"""
monthly_status.py — Generate and send a Gurbani Path monthly status email.

Triggered by .github/workflows/monthly-status.yml on the 1st of each month.
Reads recent git history and the roadmap doc, composes a plain-text email,
and sends it via Gmail SMTP.

Required environment variables:
  GMAIL_USER          sender Gmail address (e.g. jssbox@gmail.com)
  GMAIL_APP_PASSWORD  16-char Gmail App Password (NOT your regular password —
                      generate at https://myaccount.google.com/apppasswords)
  DEST_EMAIL          recipient email (typically same as GMAIL_USER)

Optional:
  DRY_RUN=1           print the email to stdout but don't actually send

Local test:
  GMAIL_USER=you@gmail.com \\
  GMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxx \\
  DEST_EMAIL=you@gmail.com \\
  DRY_RUN=1 \\
  python3 scripts/monthly_status.py
"""

import os
import re
import smtplib
import subprocess
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://gurbanipath.org"
REPO_URL = "https://github.com/jaswind/gurbanipath"
ROADMAP_PATH = REPO_ROOT / "_docs" / "ENHANCEMENTS-ROADMAP.md"


def get_commits_last_30_days():
    """Return list of (date, short_message) tuples for last 30 days of commits."""
    since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "log",
             f"--since={since}",
             "--pretty=format:%ad|%s",
             "--date=short"],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"git log failed: {e.stderr}")
        return []

    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        date, _, msg = line.partition("|")
        # Use only the subject line, not the multi-line body
        subject = msg.split("\n")[0].strip()
        commits.append((date, subject))
    return commits


def parse_roadmap_pipeline():
    """Extract Tier 1 (in-pipeline) user stories from the roadmap doc."""
    if not ROADMAP_PATH.exists():
        return []

    text = ROADMAP_PATH.read_text(encoding="utf-8")

    # Find the TIER 1 section
    tier1_match = re.search(
        r"## TIER 1.*?(?=## TIER 2|\Z)", text, re.DOTALL
    )
    if not tier1_match:
        return []
    tier1 = tier1_match.group(0)

    # Extract: ### US-N: Title  followed by the "As ... I want ... so that" block
    stories = []
    pattern = re.compile(
        r"### (US-\d+):\s*([^\n]+)\n\n> \*\*As\*\*\s*([^\n,]+(?:,[^\n]+)?)",
        re.MULTILINE,
    )
    for m in pattern.finditer(tier1):
        us_id = m.group(1)
        title = m.group(2).strip()
        # Strip parenthetical suffixes like "(P0 from roadmap)"
        title = re.sub(r"\s*\([^)]+\)\s*$", "", title)
        persona = m.group(3).strip().rstrip(",")
        stories.append((us_id, title, persona))
    return stories


def compose_email():
    now = datetime.now(timezone.utc)
    one_month_ago = now - timedelta(days=30)
    commits = get_commits_last_30_days()
    pipeline = parse_roadmap_pipeline()

    lines = []
    lines.append("Gurbani Path — Monthly Status")
    lines.append(f"{one_month_ago.strftime('%b %d')} to {now.strftime('%b %d, %Y')}")
    lines.append("=" * 50)
    lines.append("")

    # WHAT SHIPPED
    lines.append("SHIPPED IN THE LAST 30 DAYS")
    lines.append("-" * 50)
    if commits:
        for date, msg in commits[:40]:
            lines.append(f"  {date}  {msg}")
        if len(commits) > 40:
            lines.append(f"  ... and {len(commits) - 40} more commit(s)")
    else:
        lines.append("  (no commits in the past 30 days — quiet month)")
    lines.append("")

    # IN PIPELINE
    lines.append("IN PIPELINE (Tier 1 — next 1–3 months)")
    lines.append("-" * 50)
    if pipeline:
        for us_id, title, persona in pipeline:
            lines.append(f"  {us_id}: {title}")
            lines.append(f"        For: {persona}")
            lines.append("")
    else:
        lines.append("  (could not parse roadmap — verify _docs/ENHANCEMENTS-ROADMAP.md)")
        lines.append("")

    # LINKS
    lines.append("LINKS")
    lines.append("-" * 50)
    lines.append(f"  Live site:    {SITE_URL}")
    lines.append(f"  Repo:         {REPO_URL}")
    lines.append(f"  Full roadmap: {REPO_URL}/blob/main/_docs/ENHANCEMENTS-ROADMAP.md")
    lines.append("")
    lines.append("--")
    lines.append("Automated monthly status from the gurbanipath repository.")
    lines.append("Sent by .github/workflows/monthly-status.yml")

    body = "\n".join(lines)
    subject = f"Gurbani Path — Status {now.strftime('%Y-%m')}"
    return subject, body


def send_email(subject: str, body: str) -> None:
    gmail_user = os.environ["GMAIL_USER"]
    gmail_pw = os.environ["GMAIL_APP_PASSWORD"]
    dest = os.environ["DEST_EMAIL"]

    msg = EmailMessage()
    msg["From"] = gmail_user
    msg["To"] = dest
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_user, gmail_pw)
        smtp.send_message(msg)
    print(f"✓ Sent to {dest}: {subject}")


def main() -> None:
    # Fail fast if env is missing
    for var in ("GMAIL_USER", "GMAIL_APP_PASSWORD", "DEST_EMAIL"):
        if not os.environ.get(var):
            raise SystemExit(f"Missing required env var: {var}")

    subject, body = compose_email()

    print("=" * 60)
    print(f"Subject: {subject}")
    print("=" * 60)
    print(body)
    print("=" * 60)

    if os.environ.get("DRY_RUN"):
        print("[DRY_RUN set — skipping actual send]")
        return

    send_email(subject, body)


if __name__ == "__main__":
    main()
