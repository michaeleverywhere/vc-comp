#!/usr/bin/env python3
"""Pioneer Square Labs (PSL) portfolio scraper -> psl_companies.json
Source: https://www.psl.com/companies — Webflow CMS grid; each card links to
/companies/<slug>, carries the company name (logo alt) and an ACQUIRED flag
(visible only when acquired). Detail pages give a headline, "<YYYY>— <vehicle>"
(PSL Studio / PSL Ventures; year = first_invested), the company website,
Founder(s), Investor(s) and a description. status: acquired only when the
ACQUIRED flag is shown. No location or round published.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (webflow_pages, fetch_many, clean, tags_for, clean_url, year_of,
                             prune_substring_tags, apply_tag_overrides, is_social)
from _d20_common import write_out

SOURCE_URL = "https://www.psl.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "psl_companies.json")
PRIMARY = "Pioneer Square Labs"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "Boundless": ["Consumer"],
    "Lev": ["Future of Work"],
    "Read": ["Future of Work"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".companies-grid-item"):
            a = it.select_one("a.companies-item-link[href]")
            img = it.select_one("img.img-logo")
            if not a:
                continue
            href = urljoin(SOURCE_URL, a["href"])
            if href in seen:
                continue
            seen.add(href)
            flag = it.select_one(".acquired-flag")
            acquired = bool(flag) and "w-condition-invisible" not in (flag.get("class") or [])
            cards.append({"href": href, "name": clean(img.get("alt")) if img else None, "acquired": acquired})
    pages = fetch_many([c["href"] for c in cards], workers=6)
    out, names = [], set()
    for c in cards:
        html = pages.get(c["href"])
        headline = desc = site = meta = None
        founders, investors = None, None
        if html:
            d = BeautifulSoup(html, "html.parser")
            h = d.select_one(".company-headline")
            headline = clean(h.get_text(" ")) if h else None
            m = d.select_one("p.company-metadata.color-concrete")
            meta = clean(m.get_text(" ")) if m else None
            w = d.select_one("a.company-metadata-link[href^=http]")
            if w and not is_social(w["href"]):
                site = clean_url(w["href"])
            for box in d.select(".company-metadata-wrapper"):
                lab = box.select_one(".company-metadata-label")
                val = box.select_one("p.company-metadata")
                if lab and val:
                    l = clean(lab.get_text(" ")).lower()
                    if l.startswith("founder"):
                        founders = clean(val.get_text(" "))
                    elif l.startswith("investor"):
                        investors = clean(val.get_text(" "))
            rt = d.select_one(".rich-text-block")
            if rt:
                desc = clean(" ".join(p.get_text(" ") for p in rt.select("p"))) or None
        name = c["name"] or (c["href"].rstrip("/").rsplit("/", 1)[-1])
        if name.lower() in names:
            continue
        names.add(name.lower())
        vehicle = clean(re.sub(r"^\s*\d{4}\s*[—–-]+\s*", "", meta)) if meta else None
        out.append({
            "company_name": name,
            "description": desc or headline,
            "tagline": headline,
            "company_url": site,
            "first_invested": year_of(meta),
            "psl_vehicle": vehicle,
            "founders": founders,
            "co_investors": investors,
            "status": "acquired" if c["acquired"] else None,
            "everywhere_tags": tags_for(name, " ".join(x for x in (headline, desc) if x)),
            "primary_investor": PRIMARY,
            "profile_url": c["href"],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "first_invested", "founders", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
