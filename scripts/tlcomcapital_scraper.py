#!/usr/bin/env python3
"""TLcom Capital portfolio scraper -> tlcomcapital_companies.json
Source: https://www.tlcomcapital.com/portfolio — Webflow CMS list
(server-rendered; Webflow pagination followed). Each row carries the name,
a summary, hidden Finsweet fields (country, status Active / Exited, sector,
fund, entry-stage) and a modal whose rich text has the full description plus
Founder(s), Countries, Sector, First Check (year), Entry Stage and Website.
Entry Stage (Pre-seed / Seed / Series A / B) is TLcom's published entry
round -> stage. First Check -> first_invested.
Status: Active -> active; Exited -> acquired (raw kept in site_status).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, tags_for, clean_url, stage_label, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.tlcomcapital.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "tlcomcapital_companies.json")
PRIMARY = "TLcom Capital"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "edtech": ["Future of Work"], "healthtech": ["Health"],
    "agritech": ["CPG", "Climate / Sustainability"], "climate tech": ["Climate / Sustainability"],
    "blockchain": ["Web3 / Crypto"], "e-commerce": ["Consumer"], "hr tech": ["Future of Work"],
    "logistics": ["Logistics / Supply Chain"], "mobility": ["Transportation / Mobility"],
    "automotive tech": ["Transportation / Mobility"], "food supply": ["CPG", "Logistics / Supply Chain"],
    "data": ["Data & Analytics"], "credit": ["FinTech / Insurance"], "saas": ["Future of Work"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Knabu": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "Kola Market": ["Consumer", "Logistics / Supply Chain", "FinTech / Insurance"],
    "SeamlessHR": ["Future of Work", "FinTech / Insurance"],
    "Turnstay": ["FinTech / Insurance", "Consumer"],
    "Twiga Foods": ["Logistics / Supply Chain", "CPG", "Consumer"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for row in soup.select(".directional-list__item"):
            it = row.parent
            h = row.select_one("h2")
            name = clean(h.get_text(" ")) if h else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            f = lambda k: clean(row.select_one(f'[fs-list-field="{k}"]').get_text(" ")) if row.select_one(f'[fs-list-field="{k}"]') else None
            countries = [clean(x.get_text(" ")) for x in row.select('[fs-list-field="country"]')]
            sectors = [clean(x.get_text(" ")) for x in row.select('[fs-list-field="sector"]')]
            rt = it.select_one(".portfolio-description-richtext")
            meta, desc, site = {}, None, None
            if rt:
                p = rt.select_one("p")
                desc = clean(p.get_text(" ")) if p else None
                for li in rt.select("li"):
                    s = li.select_one("strong")
                    if not s:
                        continue
                    k = clean(s.get_text(" ")).rstrip(":").lower()
                    s.decompose()
                    meta[k] = clean(li.get_text(" "))
                    if k == "website" and li.select_one("a[href]"):
                        site = li.select_one("a[href]")["href"]
            if not desc:
                summ = row.select_one(".direcitonal-list__p")
                desc = f"{name} {clean(summ.get_text(' '))}" if summ else None
            raw_status = f("status")
            year = meta.get("first check")
            founders = [clean(x) for x in re.split(r",| and | & ", meta.get("founder(s)") or "") if clean(x)]
            out.append({
                "company_name": name,
                "description": desc,
                "company_url": clean_url(site or (("https://" + meta["website"]) if meta.get("website") and "." in meta["website"] else None)),
                "status": {"active": "active", "exited": "acquired"}.get((raw_status or "").lower()),
                "site_status": raw_status,
                "stage": stage_label(meta.get("entry stage") or f("entry-stage")),
                "first_invested": int(year) if year and re.fullmatch(r"\d{4}", year) else None,
                "location": meta.get("countries") or (", ".join(c for c in countries if c) or None),
                "fund": f("fund"),
                "founders": founders,
                "sectors": [s for s in sectors if s] or ([meta["sector"]] if meta.get("sector") else []),
                "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
            if limit and len(out) >= limit:
                break
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "stage", "first_invested", "location", "founders", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
