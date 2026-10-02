#!/usr/bin/env python3
"""White Star Capital portfolio scraper -> whitestarcapital_companies.json
Source: WP REST /wp-json/wp/v2/portfolio with ACF fields.
"""
import html as html_lib
import json, os, sys, time
from collections import Counter
from datetime import datetime, timezone

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, HEADERS, TIMEOUT

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

API = "https://whitestarcapital.com/wp-json/wp/v2/portfolio"
SOURCE_URL = "https://whitestarcapital.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "whitestarcapital_companies.json")
PRIMARY = "White Star Capital"


def fetch_all():
    rows, page = [], 1
    while True:
        r = requests.get(API, params={"per_page": 100, "page": page}, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        total_pages = int(r.headers.get("X-WP-TotalPages") or 1)
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.3)
    return rows


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    docs = fetch_all()
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for doc in docs:
        name = clean(html_lib.unescape((doc.get("title") or {}).get("rendered") or ""))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        acf = doc.get("acf") or {}
        website = clean(acf.get("external_link"))
        desc = clean(acf.get("short_description") or acf.get("hero_tagline") or acf.get("investment_content"))
        if not desc:
            content = (doc.get("content") or {}).get("rendered") or ""
            if content:
                from bs4 import BeautifulSoup
                desc = clean(BeautifulSoup(content, "html.parser").get_text(" ", strip=True))
        hq = clean(acf.get("headquarters"))
        founders = []
        fn = clean(acf.get("founder_name"))
        if fn:
            founders.append(fn)
        status = "Exited" if clean(acf.get("exited_tagline")) else "Active"
        invested = clean(acf.get("investment_date") or acf.get("initial_investment"))
        logo = None
        logo_obj = acf.get("company_logo")
        if isinstance(logo_obj, dict):
            logo = logo_obj.get("url")
        elif isinstance(logo_obj, str):
            logo = logo_obj
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "logo_url": logo,
            "status": status,
            "stage": None,
            "location": hq,
            "founders": founders or None,
            "investment_year": invested,
            "everywhere_tags": classify(name, desc)[:4],
            "primary_investor": PRIMARY,
            "source_url": doc.get("link") or SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")


if __name__ == "__main__":
    main()
