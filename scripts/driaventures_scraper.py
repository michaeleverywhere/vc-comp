#!/usr/bin/env python3
"""Dria Ventures portfolio scraper -> driaventures_companies.json
Source: https://www.dria.vc/portfolio — static host-outbound / named cards (offline capture)."""
import os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _d50_common import rec, finish

SOURCE_URL = "https://www.dria.vc/portfolio"
PRIMARY = "Dria Ventures"
# (company_name, company_url_or_None)
RAW = [
    ('Artemissecurity', 'https://artemissecurity.com'),
    ('Enigmalabs', 'https://enigmalabs.io'),
    ('Expin', 'https://expin.ai'),
    ('Junipergenomics', 'https://junipergenomics.com'),
    ('Karoohealth', 'https://karoohealth.com'),
    ('Kintow', 'https://kintow.com'),
    ('Kuberahealth', 'https://kuberahealth.com'),
    ('Longwavehq', 'https://longwavehq.com'),
    ('Olira', 'https://olira.ai'),
    ('Pitproauto', 'https://pitproauto.com'),
    ('Popcall', 'https://popcall.com'),
    ('Psyrin', 'https://psyrin.ai'),
    ('Quotient', 'https://getquotient.com'),
    ('Terial', 'https://terial.com'),
    ('Revin', 'https://revin.ai'),
    ('Ultralighthealth', 'https://ultralighthealth.com'),
    ('Doji', 'https://doji.com'),
    ('Ithgarage', 'https://ithgarage.com'),
    ('Givers', 'https://joingivers.com'),
    ('Sevenstarling', 'https://sevenstarling.com'),
    ('Teladoc', 'https://teladoc.com'),
    ('Color', 'https://color.com'),
    ('Loomhq', 'https://loomhq.com'),
    ('Pulley', 'https://pulley.com'),
    ('Samsara', 'https://samsara.com'),
    ('Grammarly', 'https://grammarly.com'),
    ('Coda', 'https://coda.io'),
    ('Audius', 'https://audius.co'),
    ('Bitwiseinvestments', 'https://bitwiseinvestments.com'),
    ('Gusto', 'https://gusto.com'),
    ('O1Labs', 'https://o1labs.org'),
    ('Stripe', 'https://stripe.com'),
    ('Papertiger', 'https://papertiger.com'),
]

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for nm, url in RAW:
        out.append(rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "driaventures", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
