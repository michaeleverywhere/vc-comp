#!/usr/bin/env python3
"""Unicorn India Ventures portfolio scraper -> unicornindiaventures_companies.json
Source: https://www.unicornivc.com/deep-tech-venture-capital-portfolio — Unicorn India Ventures (Mumbai), Indian
early-stage deep-tech venture firm. Each portfolio row gives the company name, sector, year founded, year backed
("backed since"), stage, Unicorn India fund, a description, founders and the company website."""
import os, sys, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.unicornivc.com/deep-tech-venture-capital-portfolio"
PRIMARY = "Unicorn India Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in s.select(".portfolio-item"):
        n = it.select_one(".company-summary .text-block-25")
        name = clean(n.get_text(" ", strip=True)) if n else None
        if not name:
            continue
        g = lambda sel: clean(it.select_one(sel).get_text(" ", strip=True)) if it.select_one(sel) else None
        sector, fund = g(".sector-value"), g(".fund-value")
        facts = {}
        for b in it.select(".company-details .text-block-33"):
            v = b.find_next_sibling(class_="text-block-34")
            if v:
                facts[clean(b.get_text()).lower()] = clean(v.get_text(" ", strip=True))
        desc = g(".company-details .rich-text-block")
        web = None
        for a in it.select(".company-details a[href^=http]"):
            if not is_social(a["href"]):
                web = a["href"]
                break
        founders = [clean(x.get_text()) for x in it.select(".company-details .text-block-29") if clean(x.get_text())]
        yr = lambda k: int(facts[k]) if re.fullmatch(r"(19|20)\d\d", facts.get(k) or "") else None
        out.append(rec(name, desc, web, PRIMARY, SOURCE_URL, scraped_at, sectors=[sector] if sector else [],
                       investment_stage=facts.get("stage"), founded_year=yr("founded"), first_invested_year=yr("backed since"),
                       fund=fund, founders=founders))
    if len(out) < 25:
        raise SystemExit(f"FATAL: only {len(out)} Unicorn India companies")
    finish(out, "unicornindiaventures", ("description", "company_url", "investment_stage", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
