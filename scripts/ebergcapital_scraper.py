#!/usr/bin/env python3
"""Eberg Capital portfolio scraper -> ebergcapital_companies.json
Source: https://www.eberg.capital/portfolio — static host-outbound / named cards (offline capture)."""
import os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _d50_common import rec, finish

SOURCE_URL = "https://www.eberg.capital/portfolio"
PRIMARY = "Eberg Capital"
# (company_name, company_url_or_None)
RAW = [
    ('Alt', 'https://alt.xyz'),
    ('Altsportsdata', 'https://altsportsdata.com'),
    ('Betr', 'https://betr.app'),
    ('C15', 'https://c15.studio'),
    ('Commonwealth', 'https://joincommonwealth.com'),
    ('Diamondkinetics', 'https://diamondkinetics.com'),
    ('Fantasylife', 'https://fantasylife.com'),
    ('Geminisports', 'https://geminisports.co'),
    ('Idpair', 'https://idpair.com'),
    ('Johnwallstreet', 'https://johnwallstreet.com'),
    ('Jumpshot', 'https://jumpshot.live'),
    ('Kerosports', 'https://kerosports.com'),
    ('Parcl', 'https://parcl.co'),
    ('Proleaguenetwork', 'https://proleaguenetwork.com'),
    ('Rallyrd', 'https://rallyrd.com'),
    ('Simplebet', 'https://simplebet.io'),
    ('Slamballleague', 'https://slamballleague.com'),
    ('Smarkets', 'https://smarkets.com'),
    ('Stadiumverse', 'https://stadiumverse.com'),
    ('Wagerscore', 'https://wagerscore.com'),
    ('Wagerwire', 'https://wagerwire.com'),
    ('Morphic', 'https://getmorphic.com'),
]

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for nm, url in RAW:
        out.append(rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "ebergcapital", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
