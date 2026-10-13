#!/usr/bin/env python3
"""Blume Ventures portfolio scraper -> blume_companies.json
Source: https://blume.vc/startups — schema.org ItemList of names + detail pages
for description, website, status, sector, location, founded year.
"""
import json, os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many, first_external_link,
                             prune_substring_tags, apply_tag_overrides, year_of)
from _d20_common import write_out

SOURCE_URL = "https://blume.vc/startups"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "blume_companies.json")
PRIMARY = "Blume Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for s in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(s.string or "")
        except Exception:
            continue
        graph = data.get("@graph", [data]) if isinstance(data, dict) else []
        for g in graph:
            if isinstance(g, dict) and g.get("@type") == "ItemList":
                items = g.get("itemListElement") or []
                break
        if items:
            break
    out, seen = [], set()
    detail_urls = []
    for it in items:
        name = clean(it.get("name"))
        detail = it.get("url")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        detail_urls.append(detail)
        out.append({
            "company_name": name,
            "description": None,
            "company_url": None,
            "sectors": [],
            "location": None,
            "status": None,
            "first_invested": None,
            "detail_url": detail,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    pages = fetch_many([r["detail_url"] for r in out if r.get("detail_url")], workers=6, pause=0.12)
    for r in out:
        detail = r.pop("detail_url", None)
        html = pages.get(detail)
        if not html:
            r["everywhere_tags"] = tags_for(r["company_name"], None)
            continue
        ds = BeautifulSoup(html, "html.parser")
        md = ds.find("meta", attrs={"name": "description"})
        og = ds.find("meta", property="og:description")
        desc = clean((md.get("content") if md else None) or (og.get("content") if og else None))
        r["description"] = desc
        url = first_external_link(ds, ("blume.vc",), extra_skip=("jobs", "careers"))
        # Prefer "Website" labeled link
        for a in ds.select("a[href^=http]"):
            if clean(a.get_text(" ")) == "Website":
                url = clean_url(a["href"]) or url
                break
        r["company_url"] = clean_url(url) if url else None
        text = ds.get_text(" ", strip=True)
        if re.search(r"\bExited\b|\bExit\b", text):
            # only if status label present near Info
            if re.search(r"Info\s+Exited|Status\s+Exited|\bExited\b", text):
                r["status"] = "acquired"
        if re.search(r"Info\s+Active|\bActive\b", text) and not r.get("status"):
            r["status"] = "active"
        # sector chips often appear as "EV & Mobility , ClimateTech..."
        # leave sectors blank unless clearly labeled; tags_for uses description
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"))
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
