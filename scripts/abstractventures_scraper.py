#!/usr/bin/env python3
"""Abstract Ventures portfolio scraper -> abstractventures_companies.json
Source: https://www.abstract.com/companies-list/ — grid + all-companies-modal items.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.abstract.com/companies-list/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "abstractventures_companies.json")
PRIMARY = "Abstract Ventures"

STAGE_MAP = {
    "pre-seed": "Pre-Seed", "preseed": "Pre-Seed", "seed": "Seed",
    "series a": "Series A", "series b": "Series B", "series c": "Series C",
    "series d": "Series D", "series e": "Series E", "growth": "Growth",
}


def norm_stage(s):
    if not s:
        return None
    key = s.strip().lower()
    return STAGE_MAP.get(key, s.strip() if re.search(r"(?i)seed|series|pre-?seed|growth", s) else None)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()

    modal_by_id = {}
    for mod in soup.select("div.all-companies-modal__item[data-company-id]"):
        cid = mod.get("data-company-id")
        name = clean(mod.select_one(".all-companies-modal__item-logo-text").get_text()) if mod.select_one(".all-companies-modal__item-logo-text") else None
        desc_el = mod.select_one(".all-companies-modal__item-description")
        desc = clean(desc_el.get_text()) if desc_el else None
        sector_el = mod.select_one(".all-companies-modal__item-sector span")
        sector = clean(sector_el.get_text()) if sector_el else None
        stage_el = mod.select_one(".all-companies-modal__item-partnered span")
        stage = norm_stage(clean(stage_el.get_text()) if stage_el else None)
        website = None
        for a in mod.select("a[href^='http']"):
            href = a["href"]
            if any(x in href for x in ["abstract.com", "twitter", "linkedin", "facebook"]):
                continue
            website = clean(href)
            break
        modal_by_id[cid] = {
            "name": name, "description": desc, "sector": sector,
            "stage": stage, "website": website,
        }

    # Exited flags from grid
    exited_ids = set()
    grid_stage = {}
    for it in soup.select("div.all-companies__item[data-company-id]"):
        cid = it.get("data-company-id")
        exited_el = it.select_one(".all-companies__item-exited")
        if exited_el and clean(exited_el.get_text()):
            exited_ids.add(cid)
        stage_el = it.select_one(".all-companies__item-partnered")
        if stage_el:
            grid_stage[cid] = norm_stage(clean(stage_el.get_text()))

    out, seen = [], set()
    # Prefer modal order (complete), fallback to grid order
    order = [it.get("data-company-id") for it in soup.select("div.all-companies__item[data-company-id]")]
    for cid in order:
        info = modal_by_id.get(cid) or {}
        name = info.get("name")
        if not name:
            grid = soup.select_one(f'div.all-companies__item[data-company-id="{cid}"] h2')
            name = clean(grid.get_text()) if grid else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = info.get("description")
        website = info.get("website")
        sector = info.get("sector")
        stage = info.get("stage") or grid_stage.get(cid)
        sectors = [sector] if sector else None
        status = "acquired" if cid in exited_ids else "active"
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": stage,
            "sectors": sectors,
            "everywhere_tags": classify(name, desc, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
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
    print(f"  stage: {sum(1 for r in out if r.get('stage'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
