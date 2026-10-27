#!/usr/bin/env python3
"""Despierta Ventures portfolio scraper -> despiertaventures_companies.json
Source: WP REST https://despierta.vc/wp-json/wp/v2/portfolio"""
import html as htmlmod
import os, re, sys, time
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, TIMEOUT, clean
from _d50_common import rec, finish

SOURCE_URL = "https://despierta.vc/portfolio/"
API = "https://despierta.vc/wp-json/wp/v2/portfolio"
PRIMARY = "Despierta Ventures"


def fetch_all():
    out, page = [], 1
    while True:
        r = requests.get(API, params={"per_page": 100, "page": page}, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        out.extend(batch)
        total = int(r.headers.get("X-WP-TotalPages") or 1)
        if page >= total:
            break
        page += 1
        time.sleep(0.15)
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for p in fetch_all():
        name = clean(htmlmod.unescape((p.get("title") or {}).get("rendered") or ""))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        excerpt = BeautifulSoup((p.get("excerpt") or {}).get("rendered") or "", "html.parser").get_text(" ", strip=True)
        desc = clean(excerpt)
        # try website from content links / acf
        url = None
        acf = p.get("acf") or {}
        if isinstance(acf, dict):
            for k in ("website", "url", "company_url", "link"):
                v = acf.get(k)
                if isinstance(v, str) and v.startswith("http"):
                    url = v
                    break
        out.append(rec(name, desc, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "despiertaventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
