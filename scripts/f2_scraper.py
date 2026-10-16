#!/usr/bin/env python3
"""F2 Venture Capital portfolio scraper -> f2_companies.json
Source: https://www.f2vc.com/companies — Webflow company modals: name, sector,
acquirer (when exited), one-liner, founders, last funding round, first
partnered year, website.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, stage_label, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.f2vc.com/companies"
PRIMARY = "F2 Venture Capital"
SECTOR_MAP = {"gaming": ["Gaming / Media / Entertainment"], "cyber": ["Cybersecurity"], "cybersecurity": ["Cybersecurity"],
              "fintech": ["FinTech / Insurance"], "health": ["Health"], "data & ai": ["Data & Analytics"],
              "infrastructure": ["Dev Tools / Cloud"], "devtools": ["Dev Tools / Cloud"], "cyber security": ["Cybersecurity"],
              "insurtech": ["FinTech / Insurance"], "data enrichment": ["Data & Analytics"], "legal": ["RegTech/Gov/Legal"],
              "ai ops": ["Dev Tools / Cloud"], "devops": ["Dev Tools / Cloud"], "travel": ["Transportation / Mobility"],
              "ecommerce": ["Consumer"], "defense": ["Deeptech / Robotics / AR/VR"], "hr": ["Future of Work"],
              "mobility": ["Transportation / Mobility"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for m in soup.select(".company_modal_wrapper"):
        h2 = m.select_one("h2")
        if not h2:
            continue
        sectors = [clean(x.get_text()) for x in m.select(".sector_name") if clean(x.get_text()) and clean(x.get_text()) != "All"]
        acq = None
        ab = m.select_one(".acquired-by_layout")
        if ab and not ab.find_parent(class_="w-condition-invisible"):
            t = [clean(x.get_text()) for x in ab.select(".acquired-by-text")]
            acq = t[1] if len(t) > 1 and t[1] else (clean(ab.select_one("img").get("alt")) if ab.select_one("img") else None)
        one = m.select_one(".text-branded")
        founders = None
        for d in m.select(".inline-block"):
            if clean(d.get_text()) == "Founders:":
                nx = d.find_next_sibling("div")
                founders = [clean(x) for x in re.split(r",| & ", nx.get_text()) if clean(x)] if nx else None
        ins = {}
        for c in m.select(".company-insights-card"):
            if c.find_parent(class_="w-condition-invisible") or "w-condition-invisible" in (c.get("class") or []):
                continue
            ts = c.select(".company_modal_small_t")
            if len(ts) >= 2:
                ins[clean(ts[0].get_text()).lower()] = (c.get("href") if c.name == "a" else None) or clean(ts[1].get_text())
        lfr = ins.get("last funding round")
        out.append(rec(h2.get_text(" ", strip=True), one.get_text(" ", strip=True) if one else None, ins.get("website"),
                       PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP, founders=founders or [],
                       last_funding_round=lfr, stage=stage_label(lfr), first_invested_year=year_of(ins.get("first partnered")),
                       acquirer=acq, status="acquired" if acq else "active"))
    finish(out, "f2", ("description", "company_url", "founders", "stage", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
