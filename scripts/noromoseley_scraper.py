#!/usr/bin/env python3
"""Noro-Moseley Partners portfolio scraper -> noromoseley_companies.json
Source: https://noromoseley.com/portfolio/ — Noro-Moseley Partners, Atlanta-based venture and growth capital firm
investing in healthcare and technology companies in the Southeast and beyond. The portfolio grid gives each company's
tagline and location; each company profile page gives the name, description, website, NMP team members and the
initial investment year / exit note."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean
from _d50_common import rec, finish

SOURCE_URL = "https://noromoseley.com/portfolio/"
PRIMARY = "Noro-Moseley Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = {}
    for a in soup.select('a[href*="noromoseley.com/company/"]'):
        href = a["href"].split("#")[0]
        if href in cards:
            continue
        p = a.select_one("div.text p")
        loc = tagline = None
        if p:
            sm = p.find("small")
            loc = clean(sm.get_text(" ")) if sm else None
            if sm:
                sm.extract()
            tagline = clean(p.get_text(" "))
        if loc and re.fullmatch(r"(19|20)\d{2}", loc):
            loc = None
        cards[href] = (tagline, loc)
    pages = fetch_many(list(cards), workers=4)
    out, seen = [], set()
    for href, (tagline, loc) in cards.items():
        html = pages.get(href)
        if not html:
            continue
        s = BeautifulSoup(html, "html.parser")
        h1 = s.select_one("h1.m-hero__title")
        name = clean(h1.get_text(" ")) if h1 else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        body = s.select_one("div.profile__content")
        desc = clean(body.get_text(" ")) if body else None
        note0 = s.select_one("b.icon-list__title")
        if desc and note0 and desc == clean(note0.get_text(" ")):
            desc = None
        site = None
        if body:
            for l in body.select("a[href]"):
                h = l["href"]
                if h.startswith("http") and "noromoseley.com" not in urlparse(h).netloc:
                    site = h
                    break
        t2 = s.select_one("h2.profile__title")
        tagline = clean(t2.get_text(" ")) if t2 else tagline
        note = s.select_one("b.icon-list__title")
        note = clean(note.get_text(" ")) if note else None
        yr = re.search(r"Initial Investment in ((?:19|20)\d{2})", note or "")
        status = "Exited" if note and re.search(r"acquired|exited|ipo|merged|public|nasdaq|nyse", note, re.I) else "Active"
        team = [clean(x.get_text(" ")) for x in s.select("li.sidebar__member")]
        out.append(rec(name, desc or tagline, site, PRIMARY, SOURCE_URL, scraped_at,
                       tagline=tagline, location=loc, status=status, investment_note=note,
                       year_invested=yr.group(1) if yr else None, nmp_team=team or None, profile_url=href))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Noro-Moseley companies")
    finish(out, "noromoseley", ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
