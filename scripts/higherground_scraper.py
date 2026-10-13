#!/usr/bin/env python3
"""Higher Ground Labs portfolio scraper -> higherground_companies.json
Source: https://highergroundlabs.com/portfolio/ — JetEngine grid; names from
detail slug / img alt; ACQUIRED badge; detail pages for description + website.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many, first_external_link,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://highergroundlabs.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "higherground_companies.json")
PRIMARY = "Higher Ground Labs"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def name_from(it, detail):
    img = it.select_one("img[alt]")
    alt = clean(img.get("alt") if img else None)
    if alt and not alt.lower().startswith("logo") and "hgl" not in alt.lower() and len(alt) > 2:
        # strip "logo-" prefix variants
        alt = re.sub(r"(?i)^logo[-_ ]*", "", alt)
        if alt and alt.lower() not in ("hgl logo page",):
            return alt
    if detail:
        slug = detail.rstrip("/").split("/")[-1]
        return clean(slug.replace("-", " ").title())
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".jet-listing-grid__item"):
        a = it.select_one("a[href*='/companies/']")
        detail = urljoin(SOURCE_URL, a["href"]) if a else None
        name = name_from(it, detail)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        status = "acquired" if "ACQUIRED" in it.get_text(" ") else None
        out.append({
            "company_name": name,
            "description": None,
            "company_url": None,
            "status": status,
            "detail_url": detail,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    pages = fetch_many([r["detail_url"] for r in out if r.get("detail_url")], workers=6, pause=0.15)
    for r in out:
        detail = r.pop("detail_url", None)
        html = pages.get(detail)
        if not html:
            r["everywhere_tags"] = tags_for(r["company_name"], None)
            continue
        ds = BeautifulSoup(html, "html.parser")
        for p in ds.select(".elementor-widget-theme-post-content p, .elementor-widget-text-editor p, p"):
            t = clean(p.get_text(" "))
            if t and len(t) > 60 and "Higher Ground" not in t:
                r["description"] = t
                break
        if not r.get("description"):
            md = ds.find("meta", attrs={"name": "description"})
            if md:
                r["description"] = clean(md.get("content"))
        url = first_external_link(ds, ("highergroundlabs.com",))
        r["company_url"] = clean_url(url) if url else None
        if "ACQUIRED" in ds.get_text(" ") and not r.get("status"):
            r["status"] = "acquired"
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"))
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
