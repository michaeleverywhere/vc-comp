#!/usr/bin/env python3
"""Liberty Ventures portfolio scraper -> libertyventures_companies.json
Source: https://www.libertyventures.vc/portfolio — static capture."""
import os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _d50_common import rec, finish

SOURCE_URL = "https://www.libertyventures.vc/portfolio"
PRIMARY = "Liberty Ventures"
RAW = [
    ('Love.Life', None),
    ('Harva (formerly Supply Pay)', None),
    ('Daily Nouri', None),
    ('Notably', None),
    ('Commenda', None),
    ('B Generous', None),
    ('Levels', None),
    ('FreeCap Financial', None),
    ('Coign', None),
    ('LendKoi', None),
    ('Brief.me', None),
    ('Best Dam Tape', None),
    ('iFlip', None),
    ('DataJoint', None),
    ('Boom Supersonic', None),
    ('Angel Studios', None),
    ('EarthGrid', None),
    ('Studio companies (owned by Liberty Ventures)', None),
    ('Capitalists for Capitalism Media', None),
    ('The Right Room', None),
    ('Elsewhere', None),
    ('Community', None),
]

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = [rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at) for nm, url in RAW]
    finish(out, "libertyventures", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
