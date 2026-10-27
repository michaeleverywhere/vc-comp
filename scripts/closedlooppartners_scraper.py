#!/usr/bin/env python3
"""Closed Loop Partners portfolio scraper -> closedlooppartners_companies.json
Source: WP REST https://www.closedlooppartners.com/wp-json/wp/v2/portfolio"""
import html as htmlmod
import os, re, sys
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, TIMEOUT, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.closedlooppartners.com/portfolio"
PRIMARY = "Closed Loop Partners"
API = "https://www.closedlooppartners.com/wp-json/wp/v2/portfolio"


def fetch_all():
    out = []; page = 1
    while True:
        r = requests.get(API, params={"per_page": 100, "page": page}, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 400 and page > 1:
            break
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        out.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []; seen = set()
    for p in fetch_all():
        name = clean(htmlmod.unescape((p.get("title") or {}).get("rendered") or ""))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        excerpt = BeautifulSoup((p.get("excerpt") or {}).get("rendered") or "", "html.parser").get_text(" ", strip=True)
        desc = clean(excerpt)
        url = None
        content = (p.get("content") or {}).get("rendered") or ""
        soup = BeautifulSoup(content, "html.parser")
        for a in soup.find_all("a", href=True):
            h = a["href"].strip()
            if h.startswith("http") and not is_social(h) and "closedloop" not in h.lower():
                url = h; break
        acf = p.get("acf") or {}
        if isinstance(acf, dict) and not url:
            for k in ("website", "url", "company_url", "link", "company_website"):
                v = acf.get(k)
                if isinstance(v, str) and v.startswith("http"):
                    url = v; break
        out.append(rec(name, desc, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "closedlooppartners", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
