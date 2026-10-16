#!/usr/bin/env python3
"""Gaingels portfolio scraper -> gaingels_companies.json
Source: https://gaingels.com/ — WP REST `company` post type (the data behind
gaingels.com/portfolio). ACF fields per company: website, description,
industries, co-investors, exited / exit type, investment round(s), and the
post-money valuation of the round Gaingels joined (financing as published).
"""
import json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, html_text, stage_label
from _d50_common import rec, finish, wp_all

ORIGIN = "https://gaingels.com"
SOURCE_URL = "https://gaingels.com/portfolio/"
PRIMARY = "Gaingels"
SECTOR_MAP = {"consumer products": ["Consumer", "CPG"], "enterprise software & services": ["Future of Work"],
              "consumer software & services": ["Consumer"], "healthcare & biotech": ["Health", "BioTech"],
              "artificial intelligence & robotics": ["Deeptech / Robotics / AR/VR"], "fintech": ["FinTech / Insurance"],
              "media": ["Gaming / Media / Entertainment"], "gaming & entertainment": ["Gaming / Media / Entertainment"],
              "space": ["Deeptech / Robotics / AR/VR"], "aviation & transportation": ["Transportation / Mobility"],
              "climate & greentech": ["Climate / Sustainability"], "digital assets & web 3.0": ["Web3 / Crypto"],
              "proptech": ["PropTech"]}
EXIT_STATUS = {"wind down": "closed", "acquired": "acquired", "ipo": "ipo", "spac": "ipo"}


def _list(v):
    if not v:
        return []
    if isinstance(v, list):
        return [clean(x) for x in v if clean(x)]
    try:
        j = json.loads(v)
        if isinstance(j, list):
            return [clean(x) for x in j if clean(x)]
    except (ValueError, TypeError):
        pass
    return [clean(x) for x in str(v).split(",") if clean(x)]


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for p in wp_all(ORIGIN, "company"):
        a = p.get("acf") or {}
        if not isinstance(a, dict):
            a = {}
        name = html_text(p["title"]["rendered"]) or clean(a.get("company"))
        rounds = _list(a.get("investment_round"))
        inds = _list(a.get("industries"))
        etypes = [x for x in _list(str(a.get("company_exit_type") or "").replace("'", '"')) if x.lower() in EXIT_STATUS]
        etype = etypes[0] if etypes else None
        pmv = clean(str(a.get("post_money_val") or "")) or None
        out.append(rec(name, html_text(a.get("description") or ""), a.get("website_url"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=inds, sector_map=SECTOR_MAP, investment_rounds=rounds,
                       stage=stage_label(rounds[0].rstrip("+")) if rounds else None,
                       post_money_valuation_usd=int(float(pmv)) if pmv and pmv.replace(".", "", 1).isdigit() else None,
                       co_investors=_list(a.get("investors")), exit_type=etype,
                       status=EXIT_STATUS.get((etype or "").lower(), "active")))
    # one company can appear once per deal; merge rounds onto the first record
    merged = {}
    for r in out:
        k = (r["company_name"] or "").lower()
        if k in merged:
            m = merged[k]
            for x in r["investment_rounds"]:
                if x not in m["investment_rounds"]:
                    m["investment_rounds"].append(x)
            for f in ("description", "company_url", "exit_type", "post_money_valuation_usd"):
                if not m.get(f) and r.get(f):
                    m[f] = r[f]
            if r["status"] != "active":
                m["status"] = r["status"]
        else:
            merged[k] = r
    out = list(merged.values())
    finish(out, "gaingels", ("description", "company_url", "stage", "post_money_valuation_usd", "everywhere_tags"))


if __name__ == "__main__":
    main()
