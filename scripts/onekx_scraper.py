#!/usr/bin/env python3
"""1kx portfolio scraper -> onekx_companies.json
Source: https://1kx.capital/portfolio — Next.js page rendered server-side; each
<li class="portfolio-card"> links to the company website and shows the year
1kx invested (portfolio-card__year), a category (feature cards only) or a status label (Invested / Exited; kept
verbatim in site_status, not mapped to a lead status), the name and a
one-line description. No location, round or
status published.
"""
import os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, year_of, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://1kx.capital/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "onekx_companies.json")
PRIMARY = "1kx"
# 1kx is a crypto fund: every portfolio company is onchain / web3.
SECTOR_TAG_MAP = {
    "infrastructure": ["Web3 / Crypto"], "onchain finance": ["Web3 / Crypto", "FinTech / Insurance"],
    "consumer": ["Web3 / Crypto", "Consumer"], "gaming": ["Web3 / Crypto", "Gaming / Media / Entertainment"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select("li.portfolio-card"):
        n = it.select_one(".portfolio-card__name")
        name = clean(n.get_text(" ")) if n else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        d = it.select_one(".portfolio-card__inline-desc, .portfolio-card__desc")
        desc = clean(d.get_text(" ")) if d else None
        cat = it.select_one(".portfolio-card__category")
        sectors = [clean(cat.get_text(" "))] if cat and clean(cat.get_text(" ")) else []
        yr = it.select_one(".portfolio-card__year")
        a = it.select_one("a[href]")
        st = it.select_one(".portfolio-card__status-label")
        st = clean(st.get_text(" ")) if st else None
        tags = tags_for(name, desc, sectors, SECTOR_TAG_MAP)
        if "Web3 / Crypto" not in tags:
            tags = (["Web3 / Crypto"] + tags)[:4]
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a["href"]) if a else None,
            "sectors": sectors,
            "first_invested": year_of(yr.get_text(" ")) if yr else None,
            "site_status": st,
            "everywhere_tags": tags,
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
