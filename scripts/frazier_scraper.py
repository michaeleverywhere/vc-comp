#!/usr/bin/env python3
"""Frazier Life Sciences portfolio scraper -> frazier_companies.json
Source: https://frazierls.com/portfolio/ — company modals: name (logo alt),
website, description paragraphs, exit note, Status, Therapeutic Area, Modality,
Year Invested.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, year_of, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://frazierls.com/portfolio/"
PRIMARY = "Frazier Life Sciences"
SECTOR_MAP = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for h in soup.find_all("h6", string=re.compile(r"^\s*Status\s*$")):
        card = h
        while card is not None and not (card.find("img", alt=True) and card.find("a", string=re.compile("Visit Website"))
                                        or (card.find("img", alt=True) and len(card.find_all("h6")) >= 3 and card.find("p") and card.name == "div" and card.find("img", alt=True).get("alt") not in ("linked in",))):
            card = card.parent
        if card is None:
            continue
        img = [i for i in card.find_all("img", alt=True) if i["alt"] not in ("linked in", "")]
        if not img:
            continue
        facts = {}
        for h6 in card.find_all("h6"):
            p = h6.find_next_sibling("p")
            if p:
                facts[clean(h6.get_text(strip=True)).lower()] = clean(p.get_text(" ", strip=True))
        paras = [clean(p.get_text(" ", strip=True)) for p in card.find_all("p") if not p.find_previous_sibling("h6")
                 and not (p.parent and p.parent.find("h6"))]
        paras = [p for p in paras if p]
        note = next((p for p in paras if re.match(r"^(Acquired|IPO|Merged|Public)", p)), None)
        desc = " ".join(p for p in paras if p != note) or None
        site = None
        for a in card.find_all("a", href=True):
            if a["href"].startswith("http") and "frazierls" not in a["href"] and not is_social(a["href"]):
                site = a["href"]; break
        st = (facts.get("status") or "").lower()
        acq = None
        m = re.match(r"Acquired by (.+?)(?: in ((?:19|20)\d\d))?\.?$", note or "")
        if m:
            acq = m.group(1).strip()
        out.append(rec(img[0]["alt"], desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x for x in (facts.get("therapeutic area"), facts.get("modality")) if x],
                       sector_map={(facts.get("therapeutic area") or "").lower(): ["BioTech", "Health"]},
                       therapeutic_area=facts.get("therapeutic area"), modality=facts.get("modality"),
                       first_invested_year=year_of(facts.get("year invested")), exit_note=note, acquirer=acq,
                       status=("acquired" if "acquired" in st else "ipo" if ("ipo" in st or "public" in st) else "active" if st == "private" else (st or None)),
                       status_detail=facts.get("status")))
    finish(out, "frazier", ("description", "company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
