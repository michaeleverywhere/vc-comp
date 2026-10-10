#!/usr/bin/env python3
"""VentureFriends portfolio scraper -> venturefriends_companies.json
Source: https://www.venturefriends.vc/portfolio — Webflow CMS grid
(`.portfolio-collection-item`, paginated `?<hash>_page=N`) with a hidden
`fs-list-field="domain"` sector label per company. Each company's detail page
(/portfolio-companies/<slug>) has the name (page title), a headline (tagline),
a description, the website link, and a table: Founded, Location, Last funding
round. stage = "Last funding round" (only when it is a round label).
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (webflow_pages, fetch_many, clean, tags_for, clean_url, year_of, stage_label,
                             prune_substring_tags, apply_tag_overrides)

SOURCE_URL = "https://www.venturefriends.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "venturefriends_companies.json")
PRIMARY = "VentureFriends"
SECTOR_TAG_MAP = {
    "proptech": ["PropTech"], "fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"],
    "healthtech": ["Health"], "mobility": ["Transportation / Mobility"], "edtech": ["Future of Work"],
    "logistics": ["Logistics / Supply Chain"], "cybersecurity": ["Cybersecurity"], "climate": ["Climate / Sustainability"],
    "energy": ["Climate / Sustainability"], "energytech": ["Climate / Sustainability"], "gaming": ["Gaming / Media / Entertainment"], "hr tech": ["Future of Work"],
}
TAG_OVERRIDES = {}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".portfolio-collection-item.w-dyn-item"):
            a = it.select_one("a.portfolio-item-wrapper[href]")
            if not a:
                continue
            href = urljoin(SOURCE_URL, a["href"])
            if href in seen:
                continue
            seen.add(href)
            doms = [clean(x.get_text(" ")) for x in it.select("[fs-list-field=domain]") if clean(x.get_text(" "))]
            rows.append((href, doms))
    if limit:
        rows = rows[:limit]
    pages = fetch_many([h for h, _ in rows], workers=6)
    out = []
    for href, doms in rows:
        html = pages.get(href)
        if not html:
            continue
        d = BeautifulSoup(html, "html.parser")
        title = clean(d.title.get_text(" ")) if d.title else None
        name = clean(title.split("|")[0]) if title else None
        if not name:
            continue
        hd = d.select_one(".portfolio-text-info-wrapper h2")
        rt = d.select_one(".portfolio-text-info-wrapper .w-richtext")
        tagline = clean(hd.get_text(" ")) if hd else None
        desc = clean(rt.get_text(" ")) if rt else None
        f = {}
        for row in d.select(".portfolio-table-item"):
            hs = row.select("h6")
            if len(hs) >= 2:
                f[clean(hs[0].get_text(" ")).lower()] = clean(hs[1].get_text(" "))
        link = d.select_one("a.portfolio-link-out[href^=http]")
        last_round = f.get("last funding round")
        exited = "Exited" in doms or (last_round or "").lower().startswith("exited")
        doms = [x for x in doms if x != "Exited"]
        acquirer = None
        for src in (tagline, last_round):
            m = re.search(r"exited to ([^)]+?)(?:\s+(?:in\s+)?(?:19|20)\d{2})?\s*(?:\)|$)", src or "", re.I)
            if m:
                acquirer = clean(m.group(1))
                break
        out.append({
            "company_name": name,
            "description": desc or tagline,
            "tagline": tagline,
            "company_url": clean_url(link["href"]) if link else None,
            "founded_year": year_of(f.get("founded")),
            "location": f.get("location"),
            "last_funding_round": last_round,
            "stage": stage_label(last_round),
            "status": "acquired" if exited else None,
            "acquirer": acquirer,
            "sectors": doms,
            "everywhere_tags": tags_for(name, " ".join(x for x in (tagline, desc) if x), doms, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": href,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "founded_year", "location", "stage", "status", "acquirer", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
