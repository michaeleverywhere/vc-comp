#!/usr/bin/env python3
"""AirTree Ventures portfolio scraper -> airtree_companies.json
Source: https://www.airtree.vc/companies — Webflow + Finsweet CMS load/filter,
paginated via ?<hash>_page=N. Each card: sector tag(s), name, a hidden
"funding" filter value (Early-stage / Growth / Acquired / Public), a founder-
voice tagline, founded year and "Partnered" (entry round + year, e.g.
"Series A, 2019"). Each /companies/<slug> page adds a plain description and
the company's website link.
Status: Acquired -> acquired, Public -> active (listed); others null.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, fetch_many, clean, tags_for, year_of, stage_label, clean_url, apply_tag_overrides

SOURCE_URL = "https://www.airtree.vc/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "airtree_companies.json")
PRIMARY = "AirTree Ventures"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "health": ["Health"], "healthcare": ["Health"],
    "climate": ["Climate / Sustainability"], "consumer": ["Consumer"], "deep tech": ["Deeptech / Robotics / AR/VR"],
    "web3": ["Web3 / Crypto"], "marketplace": ["Consumer"], "hardware": ["Deeptech / Robotics / AR/VR"],
    "consumer & commerce": ["Consumer"], "hardware & deep tech": ["Deeptech / Robotics / AR/VR"],
    "data & infrastructure": ["Data & Analytics", "Dev Tools / Cloud"], "web3 & blockchain": ["Web3 / Crypto"],
}
OWN = ("airtree.vc", "fundpanel.io", "website-files.com")


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "DroneDeploy": ["Deeptech / Robotics / AR/VR"],
    "Go1": ["Future of Work"],
    "LawVu": ["RegTech/Gov/Legal"],
    "Legora": ["Future of Work", "RegTech/Gov/Legal"],
    "Pawshake": ["Consumer", "CPG"],
    "Paxata": ["Data & Analytics", "Dev Tools / Cloud"],
    "Process Street": [],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select("[portfolio-item].w-dyn-item"):
            nm = it.select_one("[fs-cmsfilter-field=name]")
            name = clean(nm.get_text(" ")) if nm else None
            a = it.select_one("a.cms-link[href]")
            if not name or not a or name.lower() in seen:
                continue
            seen.add(name.lower())
            fund = it.select_one("[fs-cmsfilter-field=funding]")
            grid = it.select_one(".portfolio-gridview")
            smalls = [clean(x.get_text(" ")) for x in grid.select(".text-labels-small")] if grid else []
            lv = [clean(x.get_text(" ")) for x in it.select(".portfolio-listview .text-labels-medium")]
            sectors = list(dict.fromkeys(clean(x.get_text()) for x in it.select("[fs-cmsfilter-field=sector]") if clean(x.get_text())))
            rows.append({"name": name, "href": urljoin(SOURCE_URL, a["href"]), "funding": clean(fund.get_text()) if fund else None,
                         "tagline": smalls[0] if smalls else None, "partnered": smalls[1] if len(smalls) > 1 else None,
                         "founded": year_of(lv[0]) if lv else None, "sectors": sectors})
    if limit:
        rows = rows[:limit]
    details = fetch_many([r["href"] for r in rows])
    out = []
    for r in rows:
        desc = url = None
        html = details.get(r["href"])
        if html:
            ds = BeautifulSoup(html, "html.parser")
            for inv in ds.select(".w-condition-invisible"):
                inv.decompose()
            st = [s.strip() for s in ds.stripped_strings]
            for i, s in enumerate(st[:-1]):
                if s == "Website" and len(st[i + 1]) > 30:
                    desc = clean(st[i + 1])
                    break
            for x in ds.select("a[href^=http]"):
                u = clean_url(x["href"])
                if u and not any(o in u for o in OWN):
                    url = u
                    break
        p = r["partnered"] or ""
        fnd = (r["funding"] or "").lower()
        out.append({
            "company_name": r["name"],
            "description": desc or r["tagline"],
            "tagline": r["tagline"],
            "company_url": url,
            "company_profile_url": r["href"],
            "status": "acquired" if fnd == "acquired" else ("active" if fnd == "public" else None),
            "site_status": r["funding"],
            "partnered": r["partnered"],
            "stage": stage_label(re.sub(r",?\s*(19|20)\d{2}\s*$", "", p)),
            "first_invested": year_of(p),
            "founded_year": r["founded"],
            "sectors": r["sectors"],
            "everywhere_tags": tags_for(r["name"], desc or r["tagline"], r["sectors"], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "stage", "first_invested", "founded_year", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
