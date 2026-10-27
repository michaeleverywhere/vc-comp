#!/usr/bin/env python3
"""81 Collection portfolio scraper -> 81collection_companies.json
Source: https://jobs.81collection.com/companies — getro; company name + website where published."""
import os, re, sys, requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, TIMEOUT, clean, is_social
from _d50_common import rec, finish
SOURCE_URL = "https://jobs.81collection.com/companies"
PRIMARY = "81 Collection"
SKIP = re.compile(r"(?i)^(hero|portfolio|companies|careers|jobs|team|about|81\ Collection|81)$")
def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    r = requests.get(SOURCE_URL, headers=HEADERS, timeout=TIMEOUT); r.raise_for_status()
    s = BeautifulSoup(r.text, "html.parser")
    out=[]; seen=set()
    for img in s.find_all("img", alt=True):
        nm=clean(img.get("alt"))
        if not nm or SKIP.search(nm) or len(nm)>45: continue
        if nm.lower() in seen: continue
        seen.add(nm.lower())
        url=None; a=img.find_parent("a")
        if a and a.get("href","").startswith("http") and not is_social(a["href"]): url=a["href"]
        out.append(rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 8:
        for h in s.select("h2,h3,h4"):
            nm=clean(h.get_text(" ", strip=True))
            if not nm or SKIP.search(nm) or len(nm)>45 or nm.lower() in seen: continue
            seen.add(nm.lower())
            out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "81collection", ("description", "company_url", "everywhere_tags"))
if __name__ == "__main__":
    main()
