#!/usr/bin/env python3
"""Field Ventures portfolio scraper -> fieldventures_companies.json
Source: https://www.field.vc/portfolio — static host-outbound / named cards (offline capture)."""
import os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _d50_common import rec, finish

SOURCE_URL = "https://www.field.vc/portfolio"
PRIMARY = "Field Ventures"
# (company_name, company_url_or_None)
RAW = [
    ('6Sense', 'https://6sense.com'),
    ('Bikky', 'https://bikky.com'),
    ('Blockrenovation', 'https://blockrenovation.com'),
    ('Campus', 'https://campus.edu'),
    ('Evos', 'https://getevos.ai'),
    ('Freighthero', 'https://freighthero.ai'),
    ('Indemni', 'https://indemni.com'),
    ('Iridiumcredit', 'https://iridiumcredit.com'),
    ('Superpanel', 'https://superpanel.io'),
    ('Suppli', 'https://gosuppli.com'),
    ('Datadoghq', 'https://datadoghq.com'),
    ('Upwards', 'https://upwards.com'),
    ('Rapbook', 'https://rapbook.com'),
]

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for nm, url in RAW:
        out.append(rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "fieldventures", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
