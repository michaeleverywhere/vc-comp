#!/usr/bin/env python3
"""Flare Capital Partners portfolio scraper -> flarecapital_companies.json
Source: WP REST /wp-json/wp/v2/company. Taxonomies are mirrored in class_list
(company-categories-*, company-status-*, stage-invested-*). Detail pages for
description/website when present.
"""
import os, re, sys, html as htmlmod
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, fetch_many, stage_label
from _d20_common import write_out

SOURCE_URL = "https://www.flarecapital.com/companies/"
REST = "https://www.flarecapital.com/wp-json/wp/v2/company?per_page=100&page={}"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "flarecapital_companies.json")
PRIMARY = "Flare Capital Partners"
SECTOR_MAP = {
    "tech-enabled-services": ["Health"], "provider": ["Health"], "payer": ["Health"],
    "biopharma": ["BioTech", "Health"], "consumer": ["Health", "Consumer"],
    "digital health": ["Health"],
}
TAG_OVERRIDES = {}


def class_vals(class_list, prefix):
    out = []
    for c in class_list or []:
        if c.startswith(prefix):
            out.append(c[len(prefix):].replace("-", " "))
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts, page = [], 1
    while True:
        batch = fetch(REST.format(page), as_json=True)
        if not batch:
            break
        posts += batch
        if len(batch) < 100:
            break
        page += 1
    pages = fetch_many([p.get("link") for p in posts if p.get("link")], workers=6, pause=0.15)
    out, seen = [], set()
    for p in posts:
        name = clean(htmlmod.unescape(p["title"]["rendered"]))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        cl = p.get("class_list") or []
        sectors = [s.title() for s in class_vals(cl, "company-categories-")]
        status_raw = class_vals(cl, "company-status-")
        stage_raw = class_vals(cl, "stage-invested-")
        status = None
        for s in status_raw:
            sl = s.lower()
            if sl in ("private", "active"):
                status = "active"
            elif "acquir" in sl or sl == "exited":
                status = "acquired"
            elif sl in ("public", "ipo"):
                status = "public"
        stage = None
        for s in stage_raw:
            stage = stage_label(s) or stage
        html = pages.get(p.get("link")) or ""
        soup = BeautifulSoup(html, "html.parser") if html else None
        desc = website = None
        if soup:
            for el in soup.select("article p, .entry-content p, .company-content p"):
                t = clean(el.get_text(" "))
                if t and len(t) > 40:
                    desc = t
                    break
            for a in soup.find_all("a", href=True):
                href = a["href"]
                label = (clean(a.get_text(" ")) or "").lower()
                if href.startswith("http") and "flarecapital" not in href and label in ("website", "visit website", "company website", "visit"):
                    website = clean_url(href)
                    break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": sectors,
            "stage": stage,
            "status": status,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "sectors", "stage", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
