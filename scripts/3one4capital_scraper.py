#!/usr/bin/env python3
"""3one4 Capital portfolio scraper -> 3one4capital_companies.json
Source: https://www.3one4capital.com/portfolio — Webflow + Finsweet CMS
filter, one page. Each card: company name, Entry Stage (funding round, blank
for some), Focus Area and Company Status (Active / Exited). Each
/portfolio-companies/<slug> page adds founders, co-investors, the
description and the company's website link.
Status: Active -> active, Exited -> acquired (raw kept in site_status).
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, stage_label, clean_url, apply_tag_overrides

SOURCE_URL = "https://www.3one4capital.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "3one4capital_companies.json")
PRIMARY = "3one4 Capital"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "consumer internet": ["Consumer"], "consumer tech": ["Consumer"],
    "digital health": ["Health"], "saas": ["Future of Work"], "enterprise and smb digitization": ["Future of Work"],
}


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Bugworks": ["Health", "BioTech", "Dev Tools / Cloud"],
    "CheQ": ["FinTech / Insurance"],
    "Eka.Care": ["Health"],
    "Kapiva": ["Consumer", "Logistics / Supply Chain"],
    "Kuku": ["Consumer", "Gaming / Media / Entertainment"],
    "Lokal": ["Consumer", "Gaming / Media / Entertainment", "PropTech"],
    "Lumio": ["Consumer", "Deeptech / Robotics / AR/VR"],
    "Magic Crate": ["Consumer"],
    "R for Rabbit": ["Consumer"],
    "Ripplr": ["Future of Work", "Dev Tools / Cloud", "Logistics / Supply Chain"],
    "Rozana": ["Consumer"],
    "Smallest.ai": ["Dev Tools / Cloud"],
    "Unbox Robotics": ["Future of Work", "Logistics / Supply Chain", "Deeptech / Robotics / AR/VR"],
    "Wigzo": ["Future of Work", "Dev Tools / Cloud", "Data & Analytics"],
    "Xindus": ["Logistics / Supply Chain", "RegTech/Gov/Legal"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen = [], set()
    for it in soup.select("a.pc-card"):
        g = lambda f: clean(it.select_one(f'[fs-cmsfilter-field="{f}"]').get_text(" ")) if it.select_one(f'[fs-cmsfilter-field="{f}"]') else None
        name = g("Company Name")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        rows.append({"name": name, "stage": g("Funding Round"), "focus": g("Focus Area"),
                     "status": g("Company Status"), "href": urljoin(SOURCE_URL, it["href"]) if it.get("href") else None})
        if limit and len(rows) >= limit:
            break
    details = fetch_many([r["href"] for r in rows if r["href"]])
    out = []
    for r in rows:
        founders, coinv, desc, url = [], [], None, None
        html = details.get(r["href"]) if r["href"] else None
        if html:
            ds = BeautifulSoup(html, "html.parser")
            for blk in ds.select(".pc-detail-block.internal-block"):
                head = blk.select_one(".pc-detail-head")
                head = clean(head.get_text()).lower() if head else ""
                vals = [clean(x.get_text(" ")) for x in blk.select(".w-dyn-item") if clean(x.get_text(" "))]
                if head.startswith("founder"):
                    founders = vals
                elif head.startswith("co-investor"):
                    coinv = vals
            dd = ds.select_one(".pc-description")
            desc = clean(dd.get_text(" ")) if dd else None
            for a in ds.select("a.pc-social-link[href^=http]"):
                img = a.find("img")
                if img and "website" in (img.get("src") or ""):
                    url = clean_url(a["href"])
                    break
        stt = (r["status"] or "").lower()
        sectors = [r["focus"]] if r["focus"] else []
        out.append({
            "company_name": r["name"],
            "description": desc,
            "company_url": url,
            "company_profile_url": r["href"],
            "status": "active" if stt == "active" else ("acquired" if stt == "exited" else None),
            "site_status": r["status"],
            "entry_stage": r["stage"],
            "stage": stage_label(re.sub(r"(?i)^pre series", "Pre-Series", r["stage"] or "")),
            "founders": founders,
            "co_investors": coinv,
            "sectors": sectors,
            "everywhere_tags": tags_for(r["name"], desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "stage", "founders", "co_investors", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
