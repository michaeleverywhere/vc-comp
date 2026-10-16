#!/usr/bin/env python3
"""Inventure portfolio scraper -> inventure_companies.json
Source: https://www.inventure.vc/portfolio — Webflow list (name, tagline,
country, sector) plus each venture page: status line (e.g. "Acquired by X"),
description, website, Inventure team member.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, fetch_many, clean, is_social
from _d50_common import rec, finish, page_strings

SOURCE_URL = "https://www.inventure.vc/portfolio"
PRIMARY = "Inventure"
SECTOR_MAP = {"healthtech": ["Health"], "fintech": ["FinTech / Insurance"], "consumer brand": ["Consumer"],
              "b2c marketplace": ["Consumer"], "climate": ["Climate / Sustainability"], "deeptech": ["Deeptech / Robotics / AR/VR"],
              "cybersecurity": ["Cybersecurity"], "developer tools": ["Dev Tools / Cloud"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    items = {}
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".w-dyn-item"):
            a = it.select_one("a[href^='/venture/']")
            if not a:
                continue
            link = urljoin(SOURCE_URL, a["href"])
            strs = list(dict.fromkeys(clean(x) for x in it.stripped_strings if clean(x)))
            if link not in items and strs:
                items[link] = strs
    pages = fetch_many(list(items), workers=6, pause=0.1)
    out = []
    for link, strs in items.items():
        name, tagline = strs[0], (strs[1] if len(strs) > 1 else None)
        country = strs[2] if len(strs) > 2 else None
        secs = [x.strip() for x in (strs[3] if len(strs) > 3 else "").split(",") if x.strip()]
        st, s = page_strings(pages.get(link) or "")
        desc = site = status_line = partner = entry = None
        if name in st:
            i = st.index(name, 1) if name in st[1:] else st.index(name)
            for x in st[i + 1:i + 6]:
                if re.match(r"^(€[\d.,]+m\s+)?(Pre-Seed|Seed|Series [A-Z]|Growth)( in (19|20)\d\d)?$", x):
                    entry = x
                elif re.match(r"^(Acquired|IPO|Listed|Merged|Exited|Closed)", x):
                    status_line = x
                elif len(x) > 80 and not desc:
                    desc = x
        for a in s.select("a[href^=http]") if pages.get(link) else []:
            if "inventure" not in a["href"] and not is_social(a["href"]) and "website-files" not in a["href"] and "doks.fi" not in a["href"]:
                site = a["href"]; break
        if "Inventure team" in st:
            k = st.index("Inventure team") + 1
            partner = st[k] if k < len(st) else None
        sl = (status_line or "").lower()
        out.append(rec(name, desc or tagline, site, PRIMARY, SOURCE_URL, scraped_at, sectors=secs, sector_map=SECTOR_MAP,
                       tagline=tagline, location=country, entry_round=entry,
                       stage=re.sub(r" in (19|20)\d\d$", "", entry) if entry else None,
                       first_invested_year=int(entry[-4:]) if entry and re.search(r"(19|20)\d\d$", entry) else None, lead_partner=partner, status_detail=status_line,
                       acquirer=status_line[12:].strip() if sl.startswith("acquired by") else None,
                       status=("acquired" if sl.startswith("acquired") or sl.startswith("merged") else "ipo" if sl.startswith(("ipo", "listed")) else "active"),
                       detail_url=link))
    finish(out, "inventure", ("description", "company_url", "location", "stage", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
