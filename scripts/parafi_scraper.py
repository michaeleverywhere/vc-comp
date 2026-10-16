#!/usr/bin/env python3
"""ParaFi Capital portfolio scraper -> parafi_companies.json
Source: https://parafi.com/portfolio — server-rendered (Next.js) cards
(`.portfolio-item`): company name (h2), description, category chips and
LinkedIn / X / website links ("Visit <name>'s website").
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://parafi.com/portfolio"
PRIMARY = "ParaFi Capital"
SECTOR_MAP = {"custody & wallets": ["Web3 / Crypto"], "lending & credit": ["FinTech / Insurance"],
              "gaming": ["Gaming / Media / Entertainment"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for c in soup.select(".portfolio-item"):
        h = c.find("h2")
        if not h:
            continue
        site = next((a["href"] for a in c.select("a[aria-label]") if (a.get("aria-label") or "").lower().startswith("visit")), None)
        li = next((a["href"] for a in c.select("a[aria-label]") if "linkedin" in a["href"]), None)
        tw = next((a["href"] for a in c.select("a[aria-label]") if "twitter.com" in a["href"] or "x.com" in a["href"]), None)
        p = c.find("p")
        chips = list(dict.fromkeys(clean(s.get_text(" ", strip=True)) for s in c.select("span") if clean(s.get_text())))
        out.append(rec(h.get_text(" ", strip=True), p.get_text(" ", strip=True) if p else None, site, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=chips, sector_map=SECTOR_MAP, linkedin_url=li, twitter_url=tw))
    finish(out, "parafi", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
