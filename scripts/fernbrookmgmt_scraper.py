#!/usr/bin/env python3
"""Fernbrook Capital Management portfolio scraper -> fernbrookmgmt_companies.json
Source: https://fernbrookmgmt.com/investments — chrome-dom head extract; company name + website where published."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom
SOURCE_URL = "https://fernbrookmgmt.com/investments"
PRIMARY = "Fernbrook Capital Management"

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = dom(SOURCE_URL, 18000, min_len=2000)
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "noscript"]):
        t.decompose()
    out = []; seen = set()
    # Prefer h-tagged company names in investment cards
    for h in s.select("h1, h2, h3, h4, h5, h6, .portfolio-title, .company-name, strong"):
        nm = clean(h.get_text(" ", strip=True))
        if not nm or len(nm) > 45 or len(nm.split()) > 6: continue
        if re.search(r"(?i)^(investments?|portfolio|home|about|contact|news|blog|careers|privacy|terms)$", nm): continue
        if nm.lower() in seen: continue
        seen.add(nm.lower())
        url = None
        card = h.parent
        if card:
            for a in card.find_all("a", href=True):
                href = a["href"].strip()
                if href.startswith("http") and not is_social(href) and "fernbrook" not in href.lower():
                    url = href; break
        out.append(rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "fernbrookmgmt", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
