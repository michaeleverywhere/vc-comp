#!/usr/bin/env python3
"""Connect Ventures portfolio scraper -> connect_companies.json
Source: https://www.connectventures.co/companies — Webflow CMS list, paginated
(`?<hash>_page=N`). Each card carries the name, Finsweet filter fields
(category x N, location = country, invested year, status Active / Acquired /
Retired) and a one-line description. Detail pages (/companies/<slug>) add a
longer description, the company website and founder names.
status: Acquired -> acquired, Active -> active; "Retired" kept in site_status
only. Location is the country the site lists (no city published).
"""
import json, os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (webflow_pages, fetch_many, clean, tags_for, clean_url, year_of,
                             prune_substring_tags, apply_tag_overrides, is_social)

SOURCE_URL = "https://www.connectventures.co/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "connect_companies.json")
PRIMARY = "Connect Ventures"
SECTOR_TAG_MAP = {
    "biotech": ["BioTech"], "fintech": ["FinTech / Insurance"], "health": ["Health"],
    "robotics": ["Deeptech / Robotics / AR/VR"], "deep tech": ["Deeptech / Robotics / AR/VR"],
    "infrastructure": ["Dev Tools / Cloud"], "consumer": ["Consumer"],
}
TAG_OVERRIDES = {}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".cms-portfolio-item.w-dyn-item"):
            a = it.select_one("a.portfolio-item-wrapper[href]")
            nm = it.select_one("[fs-cmsfilter-field=name]")
            if not a or not nm:
                continue
            href = urljoin(SOURCE_URL, a["href"])
            if href in seen:
                continue
            seen.add(href)
            cats = [clean(x.get_text(" ")) for x in it.select("[fs-cmsfilter-field=category]") if clean(x.get_text(" "))]
            loc = it.select_one("[fs-cmsfilter-field=location]")
            yr = it.select_one("[fs-cmsfilter-field=year]")
            st = it.select_one("[fs-cmsfilter-field=status]")
            ds = it.select_one(".portfolio-details > .text")
            rows.append({
                "company_name": clean(nm.get_text(" ")),
                "tagline": clean(ds.get_text(" ")) if ds else None,
                "categories": cats,
                "location": clean(loc.get_text(" ")) if loc else None,
                "first_invested": year_of(yr.get_text(" ")) if yr else None,
                "site_status": clean(st.get_text(" ")) if st else None,
                "profile_url": href,
            })
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile_url"] for r in rows], workers=6)
    out = []
    for r in rows:
        desc, site, founders = None, None, []
        html = pages.get(r["profile_url"])
        if html:
            d = BeautifulSoup(html, "html.parser")
            p = d.select_one(".company-details-wrapper p.text-l")
            desc = clean(p.get_text(" ")) if p else None
            w = d.select_one("a.company-website[href]")
            if w and not is_social(w["href"]):
                site = clean_url(w["href"])
            for x in d.select(".wrapper-company-founders-info .founder_name-position .text-bold"):
                t = clean(x.get_text(" "))
                if t and t not in founders and len(t) < 60:
                    founders.append(t)
            if not r["location"]:
                for box in d.select(".company-inner-info-div"):
                    lab = box.select_one(".text")
                    if lab and clean(lab.get_text(" ")) == "Location":
                        v = box.select_one(".h4-styling")
                        r["location"] = clean(v.get_text(" ")) if v else None
        st = (r["site_status"] or "").lower()
        rec = {
            "company_name": r["company_name"],
            "description": desc or r["tagline"],
            "tagline": r["tagline"],
            "company_url": site,
            "sectors": r["categories"],
            "location": r["location"],
            "first_invested": r["first_invested"],
            "site_status": r["site_status"],
            "status": "acquired" if st == "acquired" else ("active" if st == "active" else None),
            "founders": founders,
            "everywhere_tags": tags_for(r["company_name"], " ".join(x for x in (r["tagline"], desc) if x), r["categories"], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": r["profile_url"],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "first_invested", "location", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
