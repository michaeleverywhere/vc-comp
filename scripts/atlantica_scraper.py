#!/usr/bin/env python3
"""Atlantica Ventures portfolio scraper -> atlantica_companies.json
Source: https://atlanticaventures.com/our-companies/ — static-html extract; company name + website where published."""
import os, re, sys, requests
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, TIMEOUT, clean, is_social
from _d50_common import rec, finish
SOURCE_URL = "https://atlanticaventures.com/our-companies/"
PRIMARY = "Atlantica Ventures"
SKIP_NAME = re.compile(r"(?i)^(portfolio|companies|investments?|our companies|active|exited|team|about|news|blog|contact|home|careers|privacy|terms|all|filters?|sectors?|learn more|read more|view|see all|load more|menu|login|apply|subscribe|cookie|newsletter|lp login|jobs|hero)$")

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    r = requests.get(SOURCE_URL, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    host = urlparse(r.url).netloc.replace("www.", "")
    s = BeautifulSoup(r.text, "html.parser")
    for t in s(["script", "style", "noscript", "nav", "footer", "header"]):
        t.decompose()
    out = []; seen = set()
    for img in s.find_all("img", alt=True):
        nm = clean(img.get("alt"))
        if not nm or SKIP_NAME.search(nm) or len(nm) > 45: continue
        nm = re.sub(r"(?i)\s*logo.*$", "", nm).strip() or nm
        if nm.lower() in seen: continue
        seen.add(nm.lower())
        url = None
        a = img.find_parent("a")
        if a and a.get("href", "").startswith("http") and host.split(".")[0] not in a["href"]:
            if not is_social(a["href"]): url = a["href"]
        out.append(rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "atlantica", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
