#!/usr/bin/env python3
"""Studio VC portfolio scraper -> studiovc_companies.json
Source: https://www.studio.vc/ — the page's own inline COMPANIES array ("Companies we backed
early"): company name, Studio VC sector, outcome note (multiple / valuation / "Acquired by X" /
"Exited"), long description, plus the page's FUNDS map (Fund I / Fund II). The site lists no
company websites."""
import os, re, sys, json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.studio.vc/"
PRIMARY = "Studio VC"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "enterprise ai": [], "ai": [], "saas marketplace": [],
              "pure-play saas": [], "data": ["Data & Analytics"], "consumer tech": ["Consumer"],
              "media & tech": ["Gaming / Media / Entertainment"], "deep tech": ["Deeptech / Robotics / AR/VR"]}
ITEM = re.compile(r'\{n:"((?:[^"\\]|\\.)*)",g:"(?:[^"\\]|\\.)*",s:"((?:[^"\\]|\\.)*)",o:"((?:[^"\\]|\\.)*)",d:"((?:[^"\\]|\\.)*)"\}')


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    i = html.find("const COMPANIES")
    if i < 0:
        raise SystemExit("FATAL: COMPANIES array not found")
    block = html[i:html.find("];", i)]
    fm = re.search(r"const FUNDS=(\{.*?\});", html, re.S)
    funds = json.loads(fm.group(1)) if fm else {}
    out = []
    for n, sec, o, d in ITEM.findall(block):
        name = clean(json.loads(f'"{n}"'))
        outcome = clean(json.loads(f'"{o}"'))
        desc = clean(json.loads(f'"{d}"'))
        status, acq = None, None
        if outcome and re.search(r"(?i)acquired", outcome):
            status = "acquired"
            m = re.search(r"(?i)acquired by (.+)$", outcome)
            acq = clean(m.group(1)) if m else None
        elif outcome and re.search(r"(?i)exited", outcome):
            status = "exited"
        if not acq and desc:
            m = re.search(r"Acquired by ([A-Z][\w&.\- ]+?)[.,]", desc)
            acq = clean(m.group(1)) if m else None
            if acq and not status:
                status = "acquired"
        fund = funds.get(name)
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[clean(sec)] if sec else [],
                       sector_map=SECTOR_MAP, outcome=outcome, status=status, acquirer=acq,
                       fund=f"Fund {fund}" if fund else None))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Studio VC companies")
    finish(out, "studiovc", ("description", "sectors", "outcome", "status", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
