#!/usr/bin/env python3
"""Dallas Venture Partners portfolio scraper -> dallasventurepartners_companies.json
Source: https://www.dallasvc.com/portfolio — webflow; company name + website where published."""
import os, re, sys, requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, TIMEOUT, clean, is_social
from _d50_common import rec, finish
SOURCE_URL = "https://www.dallasvc.com/portfolio"
PRIMARY = "Dallas Venture Partners"
SKIP = re.compile(r"(?i)^(hero|portfolio|companies|careers|jobs|team|about|Dallas\ Venture\ Partners|home|contact|news|blog|insights|subscribe)$")
def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    r = requests.get(SOURCE_URL, headers=HEADERS, timeout=TIMEOUT); r.raise_for_status()
    s = BeautifulSoup(r.text, "html.parser")
    out=[]; seen=set()
    for c in s.select(".porfolio-filter_card"):
        texts=[t.strip() for t in c.stripped_strings if t.strip()]
        if not texts: continue
        desc=texts[0]
        m=re.match(r"^([A-Z0-9][\w.&\'\’+\-]*(?:\s+[A-Z][\w.&\'\’+\-]*){0,3})\s+(?:is|uses|offers|provides|operates|helps|sells|,)\b", desc)
        if not m:
            m=re.match(r"^([A-Z][\w.&\'\’+\-]*(?:\s+[A-Z0-9][\w.&\'\’+\-]*){0,2})\b", desc)
        if not m: continue
        nm=clean(m.group(1).strip().rstrip(","))
        if not nm or SKIP.search(nm) or nm.lower() in seen: continue
        seen.add(nm.lower())
        out.append(rec(nm, desc if len(desc)<=400 else desc[:397]+"...", None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "dallasventurepartners", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
