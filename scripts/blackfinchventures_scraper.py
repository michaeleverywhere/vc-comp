#!/usr/bin/env python3
"""Blackfinch Ventures portfolio scraper -> blackfinchventures_companies.json
Source: https://www.blackfinch.ventures/portfolio — Blackfinch Ventures, the UK early-stage venture capital arm of
Blackfinch Group (EIS/SEIS funds) investing in tech-enabled startups. Each portfolio card gives the company name
(link title), website, a short description and an "Exited" banner where applicable."""
import os, sys, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.blackfinch.ventures/portfolio"
PRIMARY = "Blackfinch Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for card in soup.select("div.flip-card"):
        a = card.select_one("a.link[title]") or card.select_one("a[title]")
        name = clean(a.get("title")) if a else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        p = card.select_one(".back .text p") or card.select_one(".back p")
        pill = card.select_one(".exit-banner .pill")
        pill_t = clean(pill.get_text(" ")) if pill else None
        out.append(rec(name, clean(p.get_text(" ")) if p else None, a.get("href"), PRIMARY, SOURCE_URL, scraped_at,
                       status="Exited" if pill_t and "exit" in pill_t.lower() else "Active"))
    if len(out) < 25:
        raise SystemExit(f"FATAL: only {len(out)} Blackfinch companies")
    finish(out, "blackfinchventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
