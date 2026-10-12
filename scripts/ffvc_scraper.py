#!/usr/bin/env python3
"""ff Venture Capital portfolio scraper -> ffvc_companies.json
Source: WP REST https://ffvc.com/wp-json/wp/v2/portfolio — titles; detail pages
scraped for description + company website.
"""
import html as htmlmod
import os, re, sys, time
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (HEADERS, TIMEOUT, clean, tags_for, clean_url, fetch_many,
                             first_external_link, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://ffvc.com/portfolio/"
API = "https://ffvc.com/wp-json/wp/v2/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "ffvc_companies.json")
PRIMARY = "ff Venture Capital"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def fetch_all():
    out, page = [], 1
    while True:
        r = requests.get(API, params={"per_page": 100, "page": page, "_fields": "id,title,link"},
                         headers=HEADERS, timeout=TIMEOUT)
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
    posts = fetch_all()
    out, seen = [], set()
    details = []
    for p in posts:
        name = clean(htmlmod.unescape(p.get("title", {}).get("rendered") or ""))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        link = p.get("link")
        rec = {
            "company_name": name,
            "description": None,
            "company_url": None,
            "detail_url": link,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        details.append(link)
    pages = fetch_many([u for u in details if u], workers=8, pause=0.1)
    for r in out:
        html = pages.get(r.pop("detail_url", None))
        if html:
            ds = BeautifulSoup(html, "html.parser")
            for sel in (".elementor-widget-theme-post-content", ".entry-content", "article", "main"):
                box = ds.select_one(sel)
                if not box:
                    continue
                for p in box.select("p"):
                    t = clean(p.get_text(" "))
                    if t and len(t) > 50:
                        r["description"] = t
                        break
                if r["description"]:
                    break
            url = clean_url(first_external_link(ds, ("ffvc.com", "facebook.com", "twitter.com", "linkedin.com", "instagram.com", "youtube.com", "x.com", "efrontcloud.com", "jobs.ffvc.com")))
            if url and not any(b in url.lower() for b in ("efrontcloud.com", "jobs.ffvc.com", "ffvc.com")):
                r["company_url"] = url
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"))
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
