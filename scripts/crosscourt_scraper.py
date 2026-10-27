#!/usr/bin/env python3
"""Crosscourt portfolio scraper -> crosscourt_companies.json
Source: https://www.crosscourt.vc/portfolio — static capture."""
import os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _d50_common import rec, finish

SOURCE_URL = "https://www.crosscourt.vc/portfolio"
PRIMARY = "Crosscourt"
RAW = [
    ('Aalo Atomics', None),
    ('Albacore', None),
    ('Alljoined', None),
    ('Array Labs', None),
    ('AscendArc', None),
    ('Axiom Space', None),
    ('Bearing AI', None),
    ('Bedrock Robotics', None),
    ('Belli', None),
    ('Cedar', None),
    ('Collective', None),
    ('Dawn Aerospace', None),
    ('Drillbit', None),
    ('Epirus', None),
    ('Essential Aero', None),
    ('Figure AI', None),
    ('Firehawk Aerospace', None),
    ('Genway AI', None),
    ('GoodShip', None),
    ('Hark', None),
    ('Hermeus', None),
    ('Impulse Space', None),
    ('Industrial AI', None),
    ('Intangible', None),
    ('Jericho Security', None),
    ('Kapta Space', None),
    ('LegalOn', None),
    ('Light Links', None),
    ('Luminos AI', None),
    ('Maritime Operations Group', None),
    ('MirrorTab', None),
    ('Mothership Materials', None),
    ('Near Space Labs', None),
    ('Orca AI', None),
    ('Outpost Space', None),
    ('Path Robotics', None),
    ('PDW', None),
    ('Phantom Neuro', None),
    ('Phoenix Boring', None),
    ('Pryon', None),
    ('Rad AI', None),
    ('Red 6', None),
    ('Reliable Robotics', None),
    ('Rescale', None),
    ('Runway Financial', None),
    ('Sans String Studios', None),
    ('Schemata', None),
    ('Scout AI', None),
    ('Sky Spy', None),
    ('Skydio', None),
    ('Sollis Health', None),
    ('Spaceium', None),
    ('Spot AI', None),
    ('Standard Fleet', None),
    ('Stord', None),
    ('SwingVision', None),
    ('Unit', None),
    ('Ursa Major', None),
    ('Uthana', None),
    ('Wand AI', None),
    ('Wild West Systems', None),
    ('Wonderschool', None),
]

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = [rec(nm, None, url, PRIMARY, SOURCE_URL, scraped_at) for nm, url in RAW]
    finish(out, "crosscourt", ("description", "company_url", "everywhere_tags"))

if __name__ == "__main__":
    main()
