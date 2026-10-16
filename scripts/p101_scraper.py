#!/usr/bin/env python3
"""P101 portfolio scraper -> p101_companies.json
Source: https://p101.it/portfolio/ — WP REST `cwp_company` posts (name,
location / industry / status / fund taxonomies) plus each company page for
tagline, description, founders, website and initial-investment year.
"""
import os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_many, html_text, clean, year_of
from _d50_common import rec, finish, wp_all, wp_terms, page_strings, link_by_text

ORIGIN = "https://p101.it"
SOURCE_URL = "https://p101.it/portfolio/"
PRIMARY = "P101"
SECTOR_MAP = {"foodtech": ["CPG"], "fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"],
              "healthtech": ["Health"], "e-commerce": ["Consumer"], "ecommerce": ["Consumer"], "proptech": ["PropTech"],
              "mobility": ["Transportation / Mobility"], "saas": ["Future of Work"], "edtech": ["Consumer"],
              "cleantech": ["Climate / Sustainability"], "logistics": ["Logistics / Supply Chain"],
              "cybersecurity": ["Cybersecurity"], "deeptech": ["Deeptech / Robotics / AR/VR"], "hrtech": ["Future of Work"],
              "martech": ["Data & Analytics"], "travel": ["Transportation / Mobility"], "media": ["Gaming / Media / Entertainment"]}
STOP = {"Back to the list", "Status", "ionicons-v5-a", "Cookie policy"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "cwp_company")
    T = {k: wp_terms(ORIGIN, k) for k in ("cwp_location", "cwp_industry", "cwp_status", "cwp_fund")}
    pages = fetch_many([p["link"] for p in posts], workers=6, pause=0.1)
    out = []
    for p in posts:
        name = html_text(p["title"]["rendered"])
        strings, soup = page_strings(pages.get(p["link"]) or "")
        tagline = desc = None
        body = [s for s in strings if s not in STOP and not s.endswith("– P101")]
        if body:
            tagline = body[0]
            if len(body) > 1 and len(body[1]) > 60:
                desc = body[1]
        founders = []
        if "Founders" in strings:
            i = strings.index("Founders") + 1
            while i < len(strings) and strings[i] not in ("Team P101", "Website", "Status"):
                founders.append(strings[i]); i += 1
        inv = None
        for i, s in enumerate(strings[:-2]):
            if re.fullmatch(r"(19|20)\d{2}", s) and strings[i + 1] == "Initial":
                inv = int(s)
        names = lambda k: [T[k][i] for i in p.get(k) or [] if i in T[k]]
        st = names("cwp_status")
        out.append(rec(name, desc or tagline, link_by_text(soup, "Website ionicons-v5-a", "Website"), PRIMARY, SOURCE_URL,
                       scraped_at, sectors=names("cwp_industry"), sector_map=SECTOR_MAP, tagline=tagline,
                       location=", ".join(names("cwp_location")) or None, founders=founders,
                       fund=", ".join(names("cwp_fund")) or None, status=st[0].lower() if st else None,
                       first_invested_year=inv))
    finish(out, "p101", ("description", "company_url", "location", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
