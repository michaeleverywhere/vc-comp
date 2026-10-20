#!/usr/bin/env python3
"""SpringTime Ventures portfolio scraper -> springtimeventures_companies.json
Source: https://springtimeventures.com/portfolio/ — SpringTime's Elementor portfolio gallery: company
name, one-line description, SpringTime's categories and status (Active / Exit)."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://springtimeventures.com/portfolio/"
PRIMARY = "SpringTime Ventures"
STATUS = {"active": "active", "exit": "acquired", "exited": "acquired", "acquired": "acquired"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in s.select(".e-gallery-item"):
        t = it.select_one(".elementor-gallery-item__title")
        if not t:
            continue
        b = t.select_one("b")
        name = clean(b.get_text(" ", strip=True)) if b else None
        if not name:
            continue
        parts = [clean(x) for x in t.stripped_strings]
        parts = [x for x in parts if x and x != name]
        desc, cats, status = None, [], None
        if "Categories:" in parts:
            k = parts.index("Categories:")
            desc = " ".join(parts[:k]) or None
            tail = [clean(x) for x in " | ".join(parts[k + 1:]).split("|") if clean(x)]
            if tail and tail[-1].lower() in STATUS:
                status = tail.pop()
            cats = tail
        else:
            desc = " ".join(parts) or None
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=cats,
                       status=STATUS.get((status or "").lower()), status_label=status))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} SpringTime companies")
    finish(out, "springtimeventures", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
