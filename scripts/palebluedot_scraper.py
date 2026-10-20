#!/usr/bin/env python3
"""Pale blue dot portfolio scraper -> palebluedot_companies.json
Source: https://paleblue.vc/portfolio — portfolio cards (Next.js, read via headless Chrome; the
site answers plain HTTP clients with 429) plus each company's own Pale blue dot profile page:
company name, Pale blue dot sector, location, status (Active / Folded), tagline and description
paragraphs, website (profile "Contact" link) and founder names."""
import os, re, sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://paleblue.vc/portfolio"
PRIMARY = "Pale blue dot"


def card(a):
    name = a.select_one('[class*="portfolio-card_title"]')
    det = {}
    for it in a.select('[class*="portfolio-card_details-item"]'):
        parts = [clean(x) for x in it.stripped_strings]
        if len(parts) >= 2:
            det[parts[0].lower()] = clean(" ".join(parts[1:]))
    return clean(name.get_text(" ", strip=True)) if name else None, det, urljoin(SOURCE_URL, a.get("href"))


def profile(url):
    try:
        s = BeautifulSoup(dom(url, 9000, min_len=20000), "html.parser")
    except SystemExit:
        return {}
    m = s.find("main") or s
    site = m.select_one('a[class*="page-portfolio_intro-info-items-link"]')
    paras, founders, in_f = [], [], False
    for p in m.find_all("p"):
        if p.find_parent("a", href=re.compile(r"^/portfolio/")):
            continue
        t = clean(p.get_text(" ", strip=True))
        if not t:
            continue
        if t == "Founders":
            in_f = True
            continue
        if in_f:
            if t.lower() == "linkedin":
                continue
            n = p.select_one("span.typography-headline-xs")
            n = clean(n.get_text(" ", strip=True)) if n else None
            if n:
                founders.append(n)
        else:
            paras.append(t)
    href = site.get("href") if site else None
    return {"website": None if (not href or is_social(href)) else href,
            "tagline": paras[0] if paras else None,
            "description": " ".join(paras[1:]) if len(paras) > 1 else (paras[0] if paras else None),
            "founders": founders}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=50000), "html.parser")
    cards = [card(a) for a in s.select('a[class*="portfolio-list_list-card"]')]
    cards = [c for c in cards if c[0]]
    with ThreadPoolExecutor(4) as ex:
        profs = list(ex.map(lambda c: profile(c[2]), cards))
    out = []
    for (name, det, purl), pr in zip(cards, profs):
        sector = det.get("sector")
        status = (det.get("status") or "").lower() or None
        out.append(rec(name, pr.get("description"), pr.get("website"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sector] if sector else None, tagline=pr.get("tagline"),
                       location=det.get("located"), status=status, founders=pr.get("founders") or [],
                       profile_url=purl))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Pale blue dot companies")
    finish(out, "palebluedot", ("description", "company_url", "location", "status", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
