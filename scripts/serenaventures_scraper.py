#!/usr/bin/env python3
"""Serena Ventures portfolio scraper -> serenaventures_companies.json
Source: https://serenaventures.com/portfolio — Squarespace page, name/desc/website blocks.
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://serenaventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "serenaventures_companies.json")
PRIMARY = "Serena Ventures"

SKIP = {
    "portfolio", "explore our current investments", "fund i highlights:", "fund i continued:",
    "fund ii", "fund iii", "serena ventures", "home", "about", "team", "news",
}


def is_url(line: str) -> bool:
    l = line.lower().strip()
    return bool(re.match(r"^(https?://)?(www\.)?[a-z0-9.-]+\.[a-z]{2,}(/\S*)?$", l))


def normalize_url(line: str) -> str:
    l = line.strip()
    if not l.startswith("http"):
        l = "https://" + l
    return l


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    # Prefer visible text stream — Squarespace often duplicates names
    lines = []
    for raw in soup.get_text("\n", strip=True).split("\n"):
        t = clean(raw)
        if not t:
            continue
        lines.append(t)

    out, seen = [], set()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.lower() in SKIP or line.lower().startswith("fund "):
            i += 1
            continue
        if is_url(line):
            i += 1
            continue
        # Candidate name: short title-like line followed by desc and/or URL
        if len(line) > 60:
            i += 1
            continue
        # Look ahead for description + url within next few lines
        desc = None
        website = None
        j = i + 1
        # sometimes name repeated
        if j < len(lines) and lines[j] == line:
            j += 1
        if j < len(lines) and not is_url(lines[j]) and lines[j].lower() not in SKIP:
            # description often starts with name again ("Esusu is a company...")
            desc = lines[j]
            j += 1
        if j < len(lines) and is_url(lines[j]):
            website = normalize_url(lines[j])
            j += 1
        if not website:
            i += 1
            continue
        name = line
        if name.lower() in seen:
            i = j
            continue
        seen.add(name.lower())
        # Clean desc if it starts with duplicated name
        if desc and desc.lower().startswith(name.lower()):
            rest = desc[len(name):].lstrip(" \u00a0")
            if rest.lower().startswith("is "):
                desc = clean(name + " " + rest)  # keep full sentence
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": "Active",
            "stage": None,
            "everywhere_tags": classify(name, desc)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break
        i = j

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")


if __name__ == "__main__":
    main()
