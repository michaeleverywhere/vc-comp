#!/usr/bin/env python3
"""Kurma Partners portfolio scraper -> kurma_companies.json
Source: https://www.kurmapartners.com/en/portfolio — server-rendered flip cards;
the back face (`.back`) gives company name (.title-name), fund
(.team-mission, e.g. "KURMA BIOFUND I"), Kurma partner and website link.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup, Comment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.kurmapartners.com/en/portfolio"
PRIMARY = "Kurma Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    out = []
    for b in soup.select(".back"):
        nm = b.select_one(".title-name")
        if not nm or not clean(nm.get_text()):
            continue
        fund = b.select_one(".team-mission")
        partner = fund.find_next_sibling("div") if fund else None
        partner = clean(partner.get_text(" ", strip=True)) if partner and not partner.find("a") else None
        a = b.select_one("a[href^=http]")
        href = a["href"] if a and not is_social(a["href"]) else None
        out.append(rec(nm.get_text(" ", strip=True), None, href, PRIMARY, SOURCE_URL, scraped_at,
                       fund=", ".join(clean(x) for x in fund.stripped_strings if clean(x)) if fund else None, kurma_partner=partner))
    finish(out, "kurma", ("company_url", "fund", "kurma_partner", "everywhere_tags"))


if __name__ == "__main__":
    main()
