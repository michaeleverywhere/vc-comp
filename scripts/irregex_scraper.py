#!/usr/bin/env python3
"""Irregular Expressions portfolio scraper -> irregex_companies.json
Source: https://www.irregex.vc/portfolio — Webflow CMS cards (Finsweet list fields):
company name, category (Tools / Security / Data / AI / Infrastructure), one-line
summary, "The Big Idea" description, founded year (card .year_founded), website ("Site" link),
exit status flag, fund vehicle (Fund I / SPV), spotlight flag and founder names."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.irregex.vc/portfolio"
PRIMARY = "Irregular Expressions"
SECTOR_MAP = {"security": ["Cybersecurity"], "tools": ["Dev Tools / Cloud"], "infrastructure": ["Dev Tools / Cloud"],
              "data": ["Data & Analytics"]}


def fv(it, f):
    el = it.select_one(f'[fs-list-field="{f}"]')
    return clean(el.get_text(" ", strip=True)) if el else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch_response(SOURCE_URL).content.decode("utf-8", "replace"), "html.parser")
    out = []
    for it in s.select(".portfolio__section__item"):
        name = fv(it, "name")
        if not name:
            continue
        cat = fv(it, "category")
        head = it.select_one(".company_card_header .w-embed")
        summary = None
        if head:
            parts = [clean(p) for p in head.get_text("|", strip=True).split("|") if clean(p) and clean(p) != "/"]
            summary = parts[-1] if len(parts) >= 3 else None
        big = it.select_one(".portfolio_card_content .portfolio_rich_text")
        site = next((a["href"] for a in it.select("a.portfolio_card_link[href]")
                     if clean(a.get_text()) == "Site" and not is_social(a["href"])), None)
        yr = it.select_one(".year_founded")
        y = re.search(r"\b(19|20)\d{2}\b", yr.get_text() if yr else "")
        exited = (fv(it, "exitstatus") or "").lower() == "true"
        founders = [clean(re.sub(r"\s+is the .*$", "", f.get_text(" ", strip=True).split(".")[0]))
                    for f in it.select(".bio-item .portfolio_rich_text")]
        out.append(rec(name, clean(big.get_text(" ", strip=True)) if big else summary, site, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=[cat] if cat else [], sector_map=SECTOR_MAP, tagline=summary,
                       founded_year=int(y.group(0)) if y else None, fund_vehicle=clean(it.get("fund_vehicle")),
                       spotlight=(fv(it, "spotlight") or "").lower() == "true",
                       founders=[f for f in founders if f and len(f.split()) <= 4],
                       status="exited" if exited else "active"))
    finish(out, "irregex", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
