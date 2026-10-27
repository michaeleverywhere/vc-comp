#!/usr/bin/env python3
"""Asymmetry Ventures portfolio scraper -> asymmetryventures_companies.json
Source: https://asymmetry.vc/portfolio/ — static capture."""
import os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _d50_common import rec, finish

SOURCE_URL = "https://asymmetry.vc/portfolio/"
PRIMARY = "Asymmetry Ventures"
RAW = [
    ('Arraylabs', 'https://arraylabs.io'),
    ('Atomicalchemy', 'https://atomicalchemy.us'),
    ('Billiontoone', 'https://billiontoone.com'),
    ('Chefrobotics', 'https://chefrobotics.ai'),
    ('Coreshell', 'https://coreshell.com'),
    ('Costplusdrugs', 'https://costplusdrugs.com'),
    ('Cyberdontics', 'https://cyberdontics.io'),
    ('Cytoreason', 'https://cytoreason.com'),
    ('Enlightra', 'https://enlightra.com'),
    ('Foresightmentalhealth', 'https://foresightmentalhealth.com'),
    ('Frontierbio', 'https://frontierbio.com'),
    ('Genecis', 'https://genecis.co'),
    ('Gmpg', 'https://gmpg.org'),
    ('Heospace', 'https://heospace.com'),
    ('Hypoint', 'https://hypoint.com'),
    ('Inpharmd', 'https://inpharmd.com'),
    ('Junokids', 'https://junokids.com'),
    ('Kernalbio', 'https://kernalbio.com'),
    ('Mastreforest', 'https://mastreforest.com'),
    ('Newculture', 'https://newculture.com'),
    ('Orbitfab', 'https://orbitfab.com'),
    ('Rejuvenationtech', 'https://rejuvenationtech.com'),
    ('Repeat', 'https://repeat.gg'),
    ('Statiq', 'https://statiq.in'),
    ('Synovalife', 'https://synovalife.com'),
    ('Turionspace', 'https://turionspace.com'),
    ('Tybrhealth', 'https://tybrhealth.com'),
    ('Viabot', 'https://viabot.com'),
]

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = [rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at) for nm, url in RAW]
    finish(out, "asymmetryventures", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
