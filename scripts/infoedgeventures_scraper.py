#!/usr/bin/env python3
"""Info Edge Ventures portfolio scraper -> infoedgeventures_companies.json
Source: https://www.infoedgeventures.in/companies — static capture."""
import os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _d50_common import rec, finish

SOURCE_URL = "https://www.infoedgeventures.in/companies"
PRIMARY = "Info Edge Ventures"
RAW = [
    ('Static', 'https://static.wixstatic.com'),
    ('30Sundays', 'https://30sundays.club'),
    ('Adda247', 'https://adda247.com'),
    ('Aftershoot', 'https://aftershoot.com'),
    ('Airblack', 'https://airblack.co'),
    ('Anscer', 'https://anscer.com'),
    ('Appsentinels', 'https://appsentinels.ai'),
    ('Ascendcap', 'https://ascendcap.in'),
    ('Attentive', 'https://attentive.ai'),
    ('Avatarlife', 'https://avatarlife.com'),
    ('Bandhoo', 'https://bandhoo.com'),
    ('Bijnis', 'https://bijnis.com'),
    ('Bluestone', 'https://bluestone.com'),
    ('Buyeazzy', 'https://buyeazzy.com'),
    ('Calculuscarbon', 'https://calculuscarbon.com'),
    ('Chattybao', 'https://chattybao.com'),
    ('Cleanelectric', 'https://cleanelectric.in'),
    ('Culture Circle', 'https://culture-circle.com'),
    ('Dgv', 'https://dgv.in'),
    ('Dotpe', 'https://dotpe.in'),
    ('Dview', 'https://dview.io'),
    ('Elchemy', 'https://elchemy.com'),
    ('Fanclash', 'https://fanclash.in'),
    ('Firsthive', 'https://firsthive.com'),
    ('Siteassets', 'https://siteassets.parastorage.com'),
]

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = [rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at) for nm, url in RAW]
    finish(out, "infoedgeventures", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
