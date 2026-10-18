#!/usr/bin/env python3
"""Jetstream portfolio scraper -> jetstream_companies.json
Source: https://www.jetstream.io/startups — server-rendered Framer page listing
"Our investments include:" as "<Company> - <one-liner>", company names linking to
their websites when Jetstream publishes one."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.jetstream.io/startups"
PRIMARY = "Jetstream"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for t in s(["script", "style", "svg"]):
        t.decompose()
    out, seen = [], set()
    for box in s.select('[data-framer-name="Company Title"]'):
        p = box.find("p") or box
        a = p.find("a", href=True)
        txt = clean(p.get_text(" ", strip=True))
        if not txt or " - " not in txt:
            continue
        name, desc = [clean(x) for x in txt.split(" - ", 1)]
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        web = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) and "jetstream.io" not in a["href"] else None
        out.append(rec(name, desc, web, PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Jetstream companies")
    finish(out, "jetstream", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
