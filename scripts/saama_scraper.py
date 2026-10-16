#!/usr/bin/env python3
"""Saama Capital portfolio scraper -> saama_companies.json
Source: https://saama.vc/portfolio/ — WordPress grid: each company tile
(`li.member-single-outer`) gives the name and sector (.member-name-btn and its
span); the following `li` holds the quick-view bio: description paragraphs,
Founder(s), Legal Name, Founded Year, Investment Year and a Website link.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://saama.vc/portfolio/"
PRIMARY = "Saama Capital"
SECTOR_MAP = {"financial services": ["FinTech / Insurance"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for li in soup.select("li.member-single-outer"):
        nb = li.select_one(".member-name-btn")
        if not nb:
            continue
        sp = nb.find("span")
        sector = clean(sp.get_text(" ", strip=True)) if sp else None
        if sp:
            sp.extract()
        name = clean(nb.get_text(" ", strip=True))
        if not name:
            continue
        desc, f, site = None, {}, None
        bio_li = li.find_next_sibling("li")
        bio = bio_li.select_one(".member-bio") if bio_li else None
        if bio:
            paras = [clean(p.get_text(" ", strip=True)) for p in bio.select(".col-12 > p")]
            desc = " ".join(p for p in paras if p) or None
            meta = bio.select_one(".text-start")
            if meta:
                txt = meta.get_text("\n", strip=True)
                for k, v in re.findall(r"(Founder\(s\)|Legal Name|Founded Year|Investment Year)\s*-\s*\n?([^\n]+)", txt):
                    f[k] = clean(v)
            a = next((a for a in bio.select(".company-links a[href]") if clean(a.get_text()) == "Website"), None)
            if a and a["href"].startswith("http") and not is_social(a["href"]):
                site = a["href"]
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, sectors=[sector] if sector else [],
                       sector_map=SECTOR_MAP, founders=f.get("Founder(s)"), legal_name=f.get("Legal Name"),
                       founded_year=year_of(f.get("Founded Year") or ""),
                       first_invested_year=year_of(f.get("Investment Year") or "")))
    finish(out, "saama", ("description", "company_url", "founded_year", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
