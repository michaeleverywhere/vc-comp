#!/usr/bin/env python3
"""Essentia Ventures portfolio scraper -> essentia_companies.json
Source: https://www.essentia.vc/portfolio/ — static host-outbound / named cards (offline capture)."""
import os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _d50_common import rec, finish

SOURCE_URL = "https://www.essentia.vc/portfolio/"
PRIMARY = "Essentia Ventures"
# (company_name, company_url_or_None)
RAW = [
    ('Loombotic', None),
    ('Workbench AI', None),
    ('Swift Navigation', None),
    ('Graphon', None),
    ('Kanu', None),
    ('Parasail', None),
    ('Coannotate', None),
    ('Tau', None),
    ('Voaige', None),
    ('TAYA', None),
    ('Intangible', None),
    ('Charter AI', None),
    ('Investing together in Industrial AI.', None),
    ('Niterra Ventures', None),
    ('Industrial technology, before the category had a name.', None),
    ('Kinetic', None),
    ('ZaiNar', None),
    ('actnano', None),
    ('Acquisitions and public listings.', None),
]

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for nm, url in RAW:
        out.append(rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "essentia", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
