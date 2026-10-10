#!/usr/bin/env python3
"""Sofinnova Partners portfolio scraper -> sofinnova_companies.json
Source: https://sofinnovapartners.com/portfolio — Next.js (Sanity-backed). The
listing page's __NEXT_DATA__ holds every company (title, slug, fund, sector,
status refs); each company page's __NEXT_DATA__ pageProps holds the resolved
fields: plainText (description), sector, fund (strategy), status (Live /
Exit), website {label,url}, and location / stage when set.
status: "Live" -> live (Sofinnova's own word); "Exit" -> acquired only when the
description says the company was acquired, otherwise blank (site_status keeps
"Exit"). stage only when the site sets a round.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, stage_label, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://sofinnovapartners.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "sofinnova_companies.json")
PRIMARY = "Sofinnova Partners"
SECTOR_TAG_MAP = {
    "biopharmaceuticals": ["BioTech", "Health"], "medical devices": ["Health"],
    "digital medicine": ["Health"], "industrial biotech": ["BioTech", "Climate / Sustainability"],
}
TAG_OVERRIDES = {}
ND = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def next_data(html):
    m = ND.search(html or "")
    return json.loads(m.group(1))["props"]["pageProps"] if m else {}


def title_of(x):
    return clean(x.get("title")) if isinstance(x, dict) else clean(x) if isinstance(x, str) else None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    listing = next_data(fetch(SOURCE_URL)).get("companies") or []
    if limit:
        listing = listing[:limit]
    urls = {c["slug"]: f"{SOURCE_URL}/{c['slug']}" for c in listing if c.get("slug")}
    pages = fetch_many(list(urls.values()), workers=6)
    out, seen = [], set()
    for c in listing:
        slug = c.get("slug")
        if not slug or slug in seen:
            continue
        seen.add(slug)
        pp = next_data(pages.get(urls[slug]))
        name = clean(pp.get("title")) or clean(c.get("title"))
        desc = clean(pp.get("plainText"))
        sector = title_of(pp.get("sector"))
        funds = [clean(f) if isinstance(f, str) else title_of(f) for f in (pp.get("fund") or [])]
        if not funds:
            funds = [title_of(f) for f in c.get("fund") or []]
        funds = [f for f in funds if f]
        st = title_of(pp.get("status"))
        web = pp.get("website") or {}
        loc = title_of(pp.get("location"))
        stage_raw = title_of(pp.get("stage"))
        acquired = (st or "").lower() == "exit" and bool(re.search(r"\bacquired\b|\bacquisition\b", desc or "", re.I))
        m = re.search(r"\bacquired by ([A-Z][\w&.\- ]{1,40}?)(?: in | for |[,.;(])", desc or "")
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(web.get("url")) if isinstance(web, dict) else None,
            "sectors": [sector] if sector else [],
            "strategy": funds,
            "location": loc,
            "stage": stage_label(stage_raw),
            "site_status": st,
            "status": "live" if (st or "").lower() == "live" else ("acquired" if acquired else None),
            "acquirer": clean(m.group(1)) if (m and acquired) else None,
            "everywhere_tags": tags_for(name, desc, [sector] if sector else [], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": urls[slug],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    # Life-sciences-only firm: keyword hits outside its plausible tag set (e.g.
    # FinTech from "reimbursement", Consumer from "patients") are noise -> dropped.
    keep = {"BioTech", "Health", "Climate / Sustainability", "Data & Analytics",
            "Deeptech / Robotics / AR/VR", "CPG", "Dev Tools / Cloud"}
    for r in out:
        r["everywhere_tags"] = [t for t in r["everywhere_tags"] if t in keep]
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "sectors", "strategy", "location", "stage", "site_status", "status", "acquirer", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
