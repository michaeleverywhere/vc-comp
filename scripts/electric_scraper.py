#!/usr/bin/env python3
"""Electric Capital portfolio scraper -> electric_companies.json
Source: https://www.electriccapital.com/ __NEXT_DATA__ homeLogoCompanies.
Caveat: homepage featured logo subset only.
"""
import os, re, sys, json
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.electriccapital.com/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "electric_companies.json")
PRIMARY = "Electric Capital"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("no __NEXT_DATA__")
    nd = json.loads(m.group(1))
    cos = ((nd.get("props") or {}).get("pageProps") or {}).get("homeLogoCompanies") or []
    out, seen = [], set()
    for c in cos:
        name = clean(c.get("name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": None,
            "company_url": None,
            "everywhere_tags": tags_for(name, None, ["Web3 / Crypto"], {"web3 / crypto": ["Web3 / Crypto"]}),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("everywhere_tags",))


if __name__ == "__main__":
    main()
