#!/usr/bin/env python3
"""Chloe Capital portfolio scraper -> chloecapital_companies.json
Source: https://www.chloecapital.com/portfolio — static host-outbound / named cards (offline capture)."""
import os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _d50_common import rec, finish

SOURCE_URL = "https://www.chloecapital.com/portfolio"
PRIMARY = "Chloe Capital"
# (company_name, company_url_or_None)
RAW = [
    ('FibrX', 'https://fibrx.io'),
    ('CLIP', 'https://clip.bike'),
    ('Airpals', 'https://airpals.co'),
    ('Greenirr', 'https://greenirr.com'),
    ('Incitu', 'https://incitu.xyz'),
    ('Ready Set Jet', 'https://readysetjetofficial.co'),
    ('Bolder Money', 'https://boldermoney.com'),
    ('Joulez', 'https://drivejoulez.com'),
    ('Lilu', 'https://wearlilu.com'),
    ('NOCTEM Health', 'https://noctemhealth.com'),
    ('Elektra Health', 'https://elektrahealth.com'),
    ('Soos', 'https://soos.org.il'),
    ('Alerje', 'https://alerje.com'),
    ('Optios', 'https://optios.ai'),
    ('Onramp', 'https://onramp.io'),
    ('Medijobs', 'https://medijobs.co'),
    ('Lua', 'https://mylua.com'),
    ('Handsdown', 'https://handsdown.shop'),
    ('Westxeast', 'https://westxeast.com'),
    ('Moodbit', 'https://mymoodbit.com'),
    ('Bonfirewomen', 'https://bonfirewomen.com'),
    ('Itselectric', 'https://itselectric.us'),
    ('Vow', 'https://vow.app'),
    ('Healthcareoriginals', 'https://healthcareoriginals.com'),
    ('Dimensionalenergy', 'https://dimensionalenergy.com'),
    ('Torigen', 'https://torigen.com'),
    ('Redswan', 'https://redswan.io'),
    ('Millionwomen', 'https://millionwomen.com'),
    ('Fluent', 'https://fluent.pet'),
    ('Designerinc', 'https://designerinc.com'),
    ('Wellbenefits', 'https://gowellbenefits.com'),
    ('Auntflow', 'https://goauntflow.com'),
    ('Talkmeup', 'https://talkmeup.co'),
    ('Blastpoint', 'https://blastpoint.com'),
    ('Careacademy', 'https://careacademy.com'),
    ('Shearshare', 'https://shearshare.com'),
    ('Basepaws', 'https://basepaws.com'),
    ('Agtechtools', 'https://agtechtools.com'),
    ('Unrulysplats', 'https://unrulysplats.com'),
    ('Coienergy', 'https://coienergy.com'),
    ('Vntana', 'https://vntana.com'),
    ('Change Finance', 'https://change-finance.com'),
    ('Wellbeing', 'https://mywellbeing.com'),
    ('Figur8Tech', 'https://figur8tech.com'),
    ('Bridgecare', 'https://getbridgecare.com'),
    ('Esmelearning', 'https://esmelearning.com'),
    ('Greencanopynode', 'https://greencanopynode.com'),
    ('Itsbyu', 'https://itsbyu.com'),
    ('Nabld', 'https://nabld.com'),
    ('Journeyfoods', 'https://journeyfoods.io'),
    ('Geospiza', 'https://geospiza.us'),
    ('Airtable', 'https://airtable.com'),
]

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for nm, url in RAW:
        out.append(rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "chloecapital", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
