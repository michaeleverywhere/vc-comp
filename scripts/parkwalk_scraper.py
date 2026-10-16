#!/usr/bin/env python3
"""Parkwalk Advisors portfolio scraper -> parkwalk_companies.json
Source: https://parkwalk.vc/portfolio/ — backed by WP REST `company` posts:
name, `sector` and `institution` (university spin-out origin) taxonomies, and
the description published as the page's meta description.
"""
import os, re, sys, html
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text
from _d50_common import rec, finish, wp_all, wp_terms

ORIGIN = "https://parkwalk.vc"
SOURCE_URL = "https://parkwalk.vc/portfolio/"
PRIMARY = "Parkwalk Advisors"
SECTOR_MAP = {"deeptech": ["Deeptech / Robotics / AR/VR"], "hardware": ["Deeptech / Robotics / AR/VR"],
              "cleantech": ["Climate / Sustainability"], "medtech": ["Health"], "life sciences": ["BioTech"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "company")
    sectors = wp_terms(ORIGIN, "sector")
    insts = wp_terms(ORIGIN, "institution")
    out = []
    for p in posts:
        m = re.search(r'<meta name="description" content="([^"]*)"', p.get("yoast_head") or "")
        desc = html.unescape(m.group(1)) if m else None
        secs = [sectors[i] for i in p.get("sector", []) if i in sectors]
        inst = [insts[i] for i in p.get("institution", []) if i in insts]
        out.append(rec(html_text(p["title"]["rendered"]), desc, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=secs, sector_map=SECTOR_MAP, institution=", ".join(inst) or None, detail_url=p["link"]))
    finish(out, "parkwalk", ("description", "institution", "everywhere_tags"))


if __name__ == "__main__":
    main()
