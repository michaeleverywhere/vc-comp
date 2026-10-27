#!/usr/bin/env python3
"""Cotu Ventures portfolio scraper -> cotuventures_companies.json
Source: https://www.cotu.vc/portfolio — static host-outbound / named cards (offline capture)."""
import os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _d50_common import rec, finish

SOURCE_URL = "https://www.cotu.vc/portfolio"
PRIMARY = "Cotu Ventures"
# (company_name, company_url_or_None)
RAW = [
    ('Careem', 'https://careem.com'),
    ('Bayzat', 'https://bayzat.com'),
    ('Kitopi', 'https://kitopi.com'),
    ('Property Finder', 'https://propertyfinder.ae'),
    ('RemotePass', 'https://remotepass.com'),
    ('Swvl', 'https://swvl.com'),
    ('Tribal', 'https://tribal.credit'),
    ('Vezeeta', 'https://vezeeta.com'),
    ('SellAnyCar', 'https://uae.sellanycar.com'),
    ('MaxAB', 'https://maxab.io'),
    ('Proximie', 'https://proximie.com'),
    ('Fresha', 'https://fresha.com'),
    ('ChatFood', 'https://chatfood.io'),
    ('Dapi', 'https://dapi.com'),
    ('DuPlays', 'https://duplays.com'),
    ('Ajar', 'https://ajar.com.kw'),
    ('Laimoon', 'https://laimoon.com'),
    ('Marti', 'https://marti.tech'),
    ('Syarah', 'https://syarah.com'),
    ('Tenderd', 'https://tenderd.com'),
    ('Wahed', 'https://wahed.com'),
]

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for nm, url in RAW:
        out.append(rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "cotuventures", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
