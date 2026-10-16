#!/usr/bin/env python3
"""Oxford Science Enterprises portfolio scraper -> ose_companies.json
Source: https://www.oxfordscienceenterprises.com/portfolio/ — company links plus
each company page: name, tagline, description, Sector, Stage, website.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, label_after, is_social
from _d50_common import rec, finish, page_strings

SOURCE_URL = "https://www.oxfordscienceenterprises.com/portfolio/"
PRIMARY = "Oxford Science Enterprises"
SECTOR_MAP = {"healthtech": ["Health"], "health tech": ["Health"], "life sciences": ["BioTech", "Health"],
              "therapeutics": ["BioTech", "Health"], "deep tech": ["Deeptech / Robotics / AR/VR"],
              "climate": ["Climate / Sustainability"], "climate tech": ["Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    links = list(dict.fromkeys(urljoin(SOURCE_URL, a["href"]) for a in soup.select("a[href^='/portfolio/']")
                               if a["href"].rstrip("/").count("/") == 2))
    pages = fetch_many(links, workers=6, pause=0.1)
    out = []
    for link in links:
        if not pages.get(link):
            continue
        st, s = page_strings(pages[link])
        name = st[0] if st else None
        i = 1 if len(st) > 1 and st[1] == name else 0
        tagline = st[i + 1] if len(st) > i + 1 and len(st[i + 1]) < 160 else None
        body = []
        for x in st[i + 2:]:
            if x == "Sector":
                break
            body.append(x)
        site = None
        for a in s.select("a[href^=http]"):
            h = a["href"]
            if "oxfordscience" not in h and not is_social(h):
                site = h; break
        sector = label_after(st, "Sector")
        stg = label_after(st, "Stage")
        out.append(rec(name, " ".join(body) or tagline, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x.strip() for x in (sector or "").split(",") if x.strip()], sector_map=SECTOR_MAP,
                       tagline=tagline, stage=stg if stg not in ("Exited", "Listed") else None,
                       status=("exited" if stg == "Exited" else "ipo" if stg == "Listed" else "active" if stg else None),
                       detail_url=link))
    finish(out, "ose", ("description", "company_url", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
