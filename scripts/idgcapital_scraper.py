#!/usr/bin/env python3
"""IDG Capital portfolio scraper -> idgcapital_companies.json
Source: WP REST https://idgcapital.com/wp-json/wp/v2/portfolio — English
permalinks only (/portfolio/ not /cn/); sector + region taxonomies via class_list.
"""
import html as htmlmod
import os, re, sys, time
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (HEADERS, TIMEOUT, clean, tags_for,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://idgcapital.com/portfolio/"
API = "https://idgcapital.com/wp-json/wp/v2/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "idgcapital_companies.json")
PRIMARY = "IDG Capital"
SECTOR_TAG_MAP = {
    "consumer technology": ["Consumer"], "consumer": ["Consumer"],
    "healthcare": ["Health", "BioTech"], "fintech/web3": ["FinTech / Insurance", "Web3 / Crypto"],
    "fintech": ["FinTech / Insurance"], "enterprise": ["Future of Work", "Dev Tools / Cloud"],
    "ai": ["Data & Analytics"], "tmt": ["Gaming / Media / Entertainment"],
}
TAG_OVERRIDES = {}


def fetch_all():
    out, page = [], 1
    while True:
        r = requests.get(API, params={"per_page": 100, "page": page, "_fields": "id,title,link,class_list"},
                         headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        out.extend(batch)
        total = int(r.headers.get("X-WP-TotalPages") or 1)
        if page >= total:
            break
        page += 1
        time.sleep(0.15)
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for p in fetch_all():
        link = p.get("link") or ""
        # English only (skip /cn/ and non-latin-only dupes when EN twin exists)
        if "/cn/" in link:
            continue
        name = clean(htmlmod.unescape(p.get("title", {}).get("rendered") or ""))
        if not name or name.lower() in seen:
            continue
        # skip pure CJK titles when an ascii twin exists later; keep mixed
        if re.fullmatch(r"[\u4e00-\u9fff\u3400-\u4dbf\s]+", name or ""):
            continue
        seen.add(name.lower())
        classes = p.get("class_list") or []
        sectors, regions = [], []
        for c in classes:
            if c.startswith("sector-") and not c.endswith("-cn"):
                lab = c.replace("sector-", "").replace("-en", "").replace("-", " ").strip()
                if lab:
                    sectors.append(lab.title())
            if c.startswith("region-") and not c.endswith("-cn"):
                lab = c.replace("region-", "").replace("-en", "").replace("-", " ").strip()
                if lab:
                    regions.append(lab.title())
        out.append({
            "company_name": name,
            "description": None,
            "sectors": sectors,
            "location": regions[0] if regions else None,
            "everywhere_tags": tags_for(name, None, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("sectors", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
