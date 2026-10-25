#!/usr/bin/env python3
"""Baseline Ventures portfolio scraper -> baselineventures_companies.json
Source: https://www.baselinev.com/investments/ — Baseline Ventures, Steve Anderson's San Francisco seed fund (first
institutional investor in Instagram, Twitter, SoFi, Figure...). The WordPress investments grid gives each company's
name (card title), short description and exit note ("IPO 2021", "Acquired by ..."); each /investment/<slug>/ page adds
the full description and the "Web:" website."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.baselinev.com/investments/"
PRIMARY = "Baseline Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = []
    for a in soup.select("div.investments-item a.item__content[href]"):
        name = clean(a.get("title") or "")
        if not name:
            continue
        d = a.select_one("p.description")
        x = a.select_one("div.acquisition-info")
        cards.append((name, urljoin(SOURCE_URL, a["href"]), clean(d.get_text(" ")) if d else None,
                      clean(x.get_text(" ")) if x else None))
    pages = fetch_many([c[1] for c in cards], workers=4)
    out, seen = [], set()
    for name, href, short, exitnote in cards:
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        desc, site = short, None
        html = pages.get(href)
        if html:
            s = BeautifulSoup(html, "html.parser")
            fd = s.select_one("p.firm-about__desc")
            if fd and clean(fd.get_text(" ")):
                desc = clean(fd.get_text(" "))
            ul = s.select_one(".firm-about__list")
            if ul:
                for st in ul.find_all("strong"):
                    if re.match(r"(?i)\s*web(site)?\s*:", st.get_text()):
                        a = st.find_next("a", href=True)
                        if a and a["href"].startswith("http") and not is_social(a["href"]):
                            site = a["href"].strip()
                        break
        status = None
        if exitnote:
            status = "Closed" if re.search(r"(?i)closed|shut|defunct", exitnote) else "Exited"
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       status=status, exit_note=exitnote, profile_url=href))
    if len(out) < 60:
        raise SystemExit(f"FATAL: only {len(out)} Baseline Ventures companies")
    finish(out, "baselineventures", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
