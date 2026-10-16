#!/usr/bin/env python3
"""DOMO Invest portfolio scraper -> domo_companies.json
Source: https://domo.vc/portfolio — WP REST `startups` (company name) with the
`teste-categoria` taxonomy as sector. No descriptions or websites in the API.
"""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text
from _d50_common import rec, finish, wp_all, wp_terms

ORIGIN = "https://domo.vc"
SOURCE_URL = ORIGIN + "/portfolio/"
PRIMARY = "DOMO Invest"
SECTOR_MAP = {"healthtech": ["Health"], "fintech": ["FinTech / Insurance"], "edtech": ["Future of Work"], "hrtech": ["Future of Work"],
              "proptech": ["PropTech"], "agtech": ["Climate / Sustainability"], "logtech": ["Logistics / Supply Chain"],
              "legaltech": ["RegTech/Gov/Legal"], "insurtech": ["FinTech / Insurance"], "retailtech": ["Consumer"],
              "mobilidade": ["Transportation / Mobility"], "mobility": ["Transportation / Mobility"],
              "setor: mobility": ["Transportation / Mobility"], "climatetech": ["Climate / Sustainability"], "energy": ["Climate / Sustainability"],
              "cybersecurity": ["Cybersecurity"], "foodtech": ["CPG"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    terms = wp_terms(ORIGIN, "teste-categoria")
    out = []
    for p in wp_all(ORIGIN, "startups"):
        secs = [terms[i] for i in p.get("teste-categoria") or [] if i in terms]
        out.append(rec(html_text(p["title"]["rendered"]), html_text(p.get("content", {}).get("rendered") or "") or None, None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=secs, sector_map=SECTOR_MAP, detail_url=p.get("link")))
    finish(out, "domo", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
