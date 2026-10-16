#!/usr/bin/env python3
"""Advent International portfolio scraper -> advent_companies.json
Source: https://www.adventinternational.com/ — WP REST `investment` (company name,
content = one-line description) with deal_type_tax, location_tax and sector_tax
taxonomies. The REST data carries no current/realized status or website.
"""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text
from _d50_common import rec, finish, wp_all, wp_terms

ORIGIN = "https://www.adventinternational.com"
SOURCE_URL = ORIGIN + "/portfolio/"
PRIMARY = "Advent International"
SECTOR_MAP = {"consumer": ["Consumer"], "consumer health": ["Health", "Consumer"], "consumer health and pharma": ["Health"],
              "consumer tech and gaming": ["Consumer", "Gaming / Media / Entertainment"], "healthcare": ["Health"],
              "financial services and technology": ["FinTech / Insurance"], "business & financial services": ["FinTech / Insurance"],
              "energy transition": ["Climate / Sustainability"], "data & information services": ["Data & Analytics"],
              "beauty and personal care": ["CPG", "Consumer"], "aerospace, defense, and space": ["Deeptech / Robotics / AR/VR"],
              "ecommerce services": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    deal, loc, sec = wp_terms(ORIGIN, "deal_type_tax"), wp_terms(ORIGIN, "location_tax"), wp_terms(ORIGIN, "sector_tax")
    out = []
    for p in wp_all(ORIGIN, "investment"):
        t = lambda m, k: [m[i] for i in p.get(k) or [] if i in m]
        desc = html_text(p.get("content", {}).get("rendered") or "") or html_text(p.get("excerpt", {}).get("rendered") or "")
        out.append(rec(html_text(p["title"]["rendered"]), desc or None, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=t(sec, "sector_tax"), sector_map=SECTOR_MAP, location=", ".join(t(loc, "location_tax")) or None,
                       deal_type=", ".join(t(deal, "deal_type_tax")) or None))
    finish(out, "advent", ("description", "location", "deal_type", "everywhere_tags"))


if __name__ == "__main__":
    main()
