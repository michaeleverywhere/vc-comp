#!/usr/bin/env python3
"""Lumira Ventures portfolio scraper -> lumira_companies.json
Source: https://www.lumiraventures.com/portfolio/ — Bootstrap modals per
company: logo alt (name), description, Industry, Headquarters, website.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.lumiraventures.com/portfolio/"
PRIMARY = "Lumira Ventures"
SECTOR_MAP = {"biotechnology": ["BioTech", "Health"], "medical devices": ["Health"], "medtech": ["Health"],
              "digital health": ["Health"], "healthcare services": ["Health"], "pharmaceuticals": ["BioTech", "Health"],
              "consumer health": ["Health", "Consumer"], "diagnostics": ["Health"], "biopharmaceutical": ["BioTech", "Health"], "medical device": ["Health"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for m in soup.select(".modal-content"):
        desc_box = m.select_one(".modal-member-desc")
        img = m.select_one(".member-img-modal img[alt]")
        if not desc_box or not img or not clean(img.get("alt")):
            continue
        ps = desc_box.select("p")
        meta_txt = ""
        desc_parts = []
        for p in ps:
            t = clean(p.get_text(" ", strip=True)) or ""
            if "Industry:" in t or "Headquarters:" in t:
                meta_txt = t
            elif t:
                desc_parts.append(t)
        ind = re.search(r"Industry:\s*(.*?)(?:\||$)", meta_txt)
        hq = re.search(r"Headquarters:\s*(.*?)(?:\||$)", meta_txt)
        a = m.select_one(".modal-btn-footer a[href^=http]")
        industry = clean(ind.group(1)) if ind else None
        out.append(rec(img["alt"], " ".join(desc_parts) or None, a["href"] if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[industry] if industry else [], sector_map=SECTOR_MAP,
                       location=clean(hq.group(1)) if hq else None))
    finish(out, "lumira", ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
