#!/usr/bin/env python3
"""First Check VC portfolio scraper -> firstcheckvc_companies.json
Source: https://www.firstcheck.vc/portfolio — WP REST /wp-json/wp/v2/company."""
import html as htmlmod, os, sys, requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, TIMEOUT, clean, is_social
from _d50_common import rec, finish
SOURCE_URL = "https://www.firstcheck.vc/portfolio"
PRIMARY = "First Check VC"
API = "https://www.firstcheck.vc/wp-json/wp/v2/company"

def fetch_all():
    out = []; page = 1
    while True:
        r = requests.get(API, params={"per_page": 100, "page": page}, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 400 and page > 1: break
        r.raise_for_status(); batch = r.json()
        if not batch: break
        out.extend(batch)
        if len(batch) < 100: break
        page += 1
    return out

def main():
    scraped_at = datetime.now(timezone.utc).isoformat(); out = []; seen = set()
    for p in fetch_all():
        name = clean(htmlmod.unescape((p.get("title") or {}).get("rendered") or ""))
        if not name or name.lower() in seen: continue
        seen.add(name.lower())
        excerpt = BeautifulSoup((p.get("excerpt") or {}).get("rendered") or "", "html.parser").get_text(" ", strip=True)
        desc = clean(excerpt); url = None
        for a in BeautifulSoup((p.get("content") or {}).get("rendered") or "", "html.parser").find_all("a", href=True):
            h = a["href"].strip()
            if h.startswith("http") and not is_social(h) and "firstcheck" not in h.lower():
                url = h; break
        out.append(rec(name, desc, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "firstcheckvc", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
