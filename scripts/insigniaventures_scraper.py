#!/usr/bin/env python3
"""Insignia Ventures Partners portfolio scraper -> insigniaventures_companies.json
Source: https://www.insignia.vc/portfolio — chrome-dom; company names from portfolio cards."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.insignia.vc/portfolio"
PRIMARY = "Insignia Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    html = dom(SOURCE_URL, 18000, min_len=5000)
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "noscript"]):
        t.decompose()
    skipre = re.compile(r"(?i)^(visit|website|learn more|read more|view|linkedin|twitter|login|jobs|careers|contact|apply|privacy|terms|portfolio|home|about|news|blog|more|exit|acquired|ipo|all)\b|^\W+$")
    seen = set()
    for a in s.select("a[href*='portfolio']"):
        h = a.select_one("h3.mt-0.title-heading, h3.title-heading, h3")
        if not h:
            continue
        nm = clean(h.get_text(" ", strip=True))
        if not nm or skipre.search(nm) or len(nm) > 50:
            continue
        k = nm.lower()
        if k in seen:
            continue
        seen.add(k)
        full = clean(a.get_text(" ", strip=True)) or ""
        desc = None
        if full.lower().startswith(nm.lower()):
            desc = full[len(nm):].strip(" -–—|")
            # strip trailing industry tag words that are short
            if desc and len(desc) > 220:
                desc = desc[:220].rsplit(" ", 1)[0]
            if desc and len(desc) < 12:
                desc = None
        # industry from card
        ind = a.select_one("div.portfolio-industry")
        sectors = [clean(ind.get_text(" ", strip=True))] if ind and clean(ind.get_text(" ", strip=True)) else None
        out.append(rec(nm, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors))
    if len(out) < 20:
        for h in s.select("h3.mt-0.title-heading, h3.title-heading"):
            nm = clean(h.get_text(" ", strip=True))
            if not nm or skipre.search(nm) or nm.lower() in seen:
                continue
            seen.add(nm.lower())
            out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "insigniaventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
