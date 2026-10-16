#!/usr/bin/env python3
"""Silver Lake portfolio scraper -> silverlake_companies.json
Source: https://www.silverlake.com/portfolio/ — WP REST `portfolio` (content =
description; acf: partner_since, website_link, fully_realized, strategy +
current/realized flag; `sectors` taxonomy).
"""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text, year_of
from _d50_common import rec, finish, wp_all, wp_terms

ORIGIN = "https://www.silverlake.com"
SOURCE_URL = "https://www.silverlake.com/portfolio/"
PRIMARY = "Silver Lake"
SECTOR_MAP = {"financial technology": ["FinTech / Insurance"], "financial market data": ["FinTech / Insurance", "Data & Analytics"],
              "electronic securities trading": ["FinTech / Insurance"], "data & analytics": ["Data & Analytics"],
              "information & data services": ["Data & Analytics"], "content & entertainment": ["Gaming / Media / Entertainment"],
              "security": ["Cybersecurity"], "security systems & technology": ["Cybersecurity"], "real estate technology": ["PropTech"],
              "mobility": ["Transportation / Mobility"], "travel technology": ["Transportation / Mobility"],
              "hr services & technology": ["Future of Work"], "infrastructure software": ["Dev Tools / Cloud"],
              "data centers & networking": ["Dev Tools / Cloud"], "semiconductors": ["Deeptech / Robotics / AR/VR"],
              "advanced manufacturing": ["Deeptech / Robotics / AR/VR"], "health & learning": ["Health"],
              "internet & ecommerce": ["Consumer"], "tech-enabled retail": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    secs = wp_terms(ORIGIN, "sectors")
    out = []
    for p in wp_all(ORIGIN, "portfolio"):
        acf = p.get("acf") or {}
        strat = acf.get("strategy_extended") or []
        strategies = [html_text((s.get("strategy") or {}).get("name") or "") for s in strat if isinstance(s, dict)]
        inv = [s.get("investment") for s in strat if isinstance(s, dict) and s.get("investment")]
        realized = bool(acf.get("fully_realized")) or bool(inv and all((x or "").startswith("prior") for x in inv))
        out.append(rec(html_text(p["title"]["rendered"]), html_text(p["content"]["rendered"]), acf.get("website_link") or None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[secs[i] for i in p.get("sectors") or [] if i in secs],
                       sector_map=SECTOR_MAP, first_invested_year=year_of(acf.get("partner_since")),
                       strategy=", ".join(x for x in strategies if x) or None,
                       investment_status=", ".join(inv) or None, status="realized" if realized else "active",
                       detail_url=p.get("link")))
    finish(out, "silverlake", ("description", "company_url", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
