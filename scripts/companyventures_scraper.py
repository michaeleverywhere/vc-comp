#!/usr/bin/env python3
"""Company Ventures portfolio scraper -> companyventures_companies.json
Source: https://www.companyventures.com/portfolio — static-html; company name + website where published."""
import os, re, sys, requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, TIMEOUT, clean, is_social
from _d50_common import rec, finish
SOURCE_URL = "https://www.companyventures.com/portfolio"
PRIMARY = "Company Ventures"
SKIP = re.compile(r"(?i)^(hero|portfolio|companies|careers|jobs|team|about|Company\ Ventures|home|contact|news|blog|insights|subscribe)$")
def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    r = requests.get(SOURCE_URL, headers=HEADERS, timeout=TIMEOUT); r.raise_for_status()
    s = BeautifulSoup(r.text, "html.parser")
    skipdom=re.compile(r"(?i)companyventures|carta|cloudflare|google|webflow|jsdelivr|cloudfront|netlify|vercel|airtable|linkedin|twitter|facebook|youtube|instagram|docs\.google|cdn\.|w3\.org")
    byd={}; out=[]; seen=set()
    for a in s.find_all("a", href=True):
        href=a["href"].strip()
        if not href.startswith("http") or is_social(href): continue
        host=re.sub(r"^www\.", "", re.sub(r"^https?://", "", href).split("/")[0].lower())
        if skipdom.search(host): continue
        texts=[t.strip() for t in a.stripped_strings if t.strip()]
        nm=None
        for t in texts:
            if 1 < len(t) <= 40 and len(t.split()) <= 5 and not re.search(r"(?i)^(visit|website|learn|read|view|more)$", t):
                nm=t; break
        if not nm:
            brand=host.split(".")[0]
            if brand and brand not in ("www","app","get","www2"):
                nm=brand.capitalize()
        if not nm: continue
        byd.setdefault(host, (nm, href))
    for nm, href in byd.values():
        nm=clean(nm)
        if not nm or SKIP.search(nm) or nm.lower() in seen: continue
        seen.add(nm.lower())
        out.append(rec(nm, None, href, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "companyventures", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
