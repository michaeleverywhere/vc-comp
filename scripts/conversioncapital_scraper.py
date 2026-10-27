#!/usr/bin/env python3
"""Conversion Capital portfolio scraper -> conversioncapital_companies.json
Source: https://conversioncapital.com/portfolio/ — static-html; company name + website where published."""
import os, re, sys, requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, TIMEOUT, clean, is_social
from _d50_common import rec, finish
SOURCE_URL = "https://conversioncapital.com/portfolio/"
PRIMARY = "Conversion Capital"
SKIP = re.compile(r"(?i)^(hero|portfolio|companies|careers|jobs|team|about|Conversion\ Capital|home|contact|news|blog|insights|subscribe)$")
def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    r = requests.get(SOURCE_URL, headers=HEADERS, timeout=TIMEOUT); r.raise_for_status()
    s = BeautifulSoup(r.text, "html.parser")
    out=[]; seen=set()
    for img in s.find_all("img", alt=True):
        nm=clean(re.sub(r"(?i)\s*logo$", "", img.get("alt") or ""))
        if not nm or SKIP.search(nm) or len(nm)>45: continue
        if nm.lower() in seen: continue
        seen.add(nm.lower())
        url=None; a=img.find_parent("a")
        if a and a.get("href","").startswith("http") and not is_social(a["href"]): url=a["href"]
        out.append(rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "conversioncapital", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
