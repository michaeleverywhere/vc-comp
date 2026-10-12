#!/usr/bin/env python3
"""Hack VC portfolio scraper -> hackvc_companies.json
Source: https://hack.vc/portfolio — SSR cards (.hc_portfolio-post) with name,
description, sector tags ((DE)FI / WEB3 INFRASTRUCTURE / AI / ...). Some marked
INVESTMENTS PRIOR TO HACK VC (kept, no status). No funding round / location.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://hack.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "hackvc_companies.json")
PRIMARY = "Hack VC"
SECTOR_TAG_MAP = {
    "(de)fi": ["Web3 / Crypto", "FinTech / Insurance"], "defi": ["Web3 / Crypto", "FinTech / Insurance"],
    "web3 infrastructure": ["Web3 / Crypto", "Dev Tools / Cloud"], "web3": ["Web3 / Crypto"],
    "ai": ["Data & Analytics"], "gaming": ["Gaming / Media / Entertainment"],
    "nft": ["Web3 / Crypto", "Gaming / Media / Entertainment"], "infrastructure": ["Dev Tools / Cloud"],
}
TAG_OVERRIDES = {}
SECTOR_LABELS = ["(DE)FI", "WEB3 INFRASTRUCTURE", "AI", "GAMING", "NFT", "INFRASTRUCTURE", "WEB3", "DEFI",
                 "INVESTMENTS PRIOR TO HACK VC"]


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for card in soup.select(".hc_portfolio-post"):
        # name: often a short heading; take first substantial text node before desc
        txt = clean(card.get_text(" "))
        if not txt:
            continue
        # strip leading "Logo Null"
        txt = re.sub(r"^Logo Null\s*", "", txt)
        sectors = []
        for lab in SECTOR_LABELS:
            if lab in txt:
                if lab != "INVESTMENTS PRIOR TO HACK VC":
                    sectors.append(lab.title() if lab.isupper() else lab)
                txt = txt.replace(lab, " ")
        txt = clean(txt)
        # pattern: Name Description
        # name is first 1-4 words before a sentence-like rest
        m = re.match(r"^([A-Za-z0-9][A-Za-z0-9 .:&'’+/-]{0,40}?)\s+([A-Z].+)$", txt or "")
        if m:
            name, desc = clean(m.group(1)), clean(m.group(2))
        else:
            # fallback: link slug
            a = card.select_one("a[href*='/portfolio/']")
            slug = None
            if a:
                mm = re.search(r"/portfolio/([^/]+)", a["href"])
                slug = mm.group(1) if mm else None
            name = clean(slug.replace("-", " ").title()) if slug else None
            desc = txt
        if not name or name.lower() in seen or name.lower() in ("logo null", "investments prior"):
            continue
        # trim name if it ate the description
        if desc and name.lower() in desc.lower()[: len(name) + 5]:
            pass
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": desc,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
