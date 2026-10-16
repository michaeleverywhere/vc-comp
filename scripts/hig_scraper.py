#!/usr/bin/env python3
"""H.I.G. Capital portfolio scraper -> hig_companies.json
Source: https://hig.com/portfolio/ — server-rendered `.portfolio--item` grid
(name h4, short description, detail link). Item classes carry status
(active/realized), fund strategy, sector and region slugs, which are mapped to
labels using the page's own filter options.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://hig.com/portfolio/"
PRIMARY = "H.I.G. Capital"
STATUS = {"active": "Active", "realized": "Realized"}
STRATEGY = {"h-i-g-realty-europe": "H.I.G. Realty Europe", "private-equity-united-states": "Private Equity - US",
            "private-equity-europe": "Private Equity - Europe", "private-equity-latin-america": "Private Equity - LatAm",
            "growth": "Growth", "h-i-g-infrastructure": "Infrastructure", "h-i-g-healthbridge": "HealthBridge"}
SECTOR = {"logistics": "Logistics", "self-storage": "Self-Storage", "real-estate": "Real Estate", "hospitality": "Hospitality",
          "transportation-logistics": "Transportation & Logistics", "education": "Education",
          "business-services": "Business Services", "chemicals": "Chemicals", "consumer-retail": "Consumer/Retail",
          "healthcare": "Healthcare", "industrials": "Industrials",
          "technology-media-and-telecom": "Technology, Media, and Telecom"}
REGION = {"north-america": "North America", "europe": "Europe", "latin-america": "Latin America"}
SECTOR_MAP = {"healthcare": ["Health"], "consumer/retail": ["Consumer"], "logistics": ["Logistics / Supply Chain"],
              "transportation & logistics": ["Logistics / Supply Chain", "Transportation / Mobility"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".portfolio--item"):
        h = it.select_one(".portfolio--item-content h4")
        if not h:
            continue
        cls = it.get("class", [])
        paras = [clean(p.get_text(" ", strip=True)) for p in it.select(".portfolio--item-content p")]
        desc = " ".join(p for p in paras if p and p.lower() != "learn more") or None
        a = it.select_one("a.portfolio--item-link[href]")
        st = next((STATUS[c] for c in cls if c in STATUS), None)
        out.append(rec(h.get_text(" ", strip=True), desc, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[SECTOR[c] for c in cls if c in SECTOR], sector_map=SECTOR_MAP,
                       region=", ".join(REGION[c] for c in cls if c in REGION) or None,
                       strategy=", ".join(STRATEGY[c] for c in cls if c in STRATEGY) or None,
                       portfolio_status=st, status={"Active": "active", "Realized": "realized"}.get(st),
                       detail_url=a["href"] if a else None))
    finish(out, "hig", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
