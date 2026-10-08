#!/usr/bin/env python3
"""Sierra Ventures portfolio scraper -> sierraventures_companies.json
Source: https://www.sierraventures.com/portfolio — HubSpot CMS page; the
"All Portfolio Companies" table is rendered client-side from an inline
`arr_obj_portfolio` JS array embedded in the page HTML. Per company: name,
description (HTML, with a "TEAM MEMBER:" heading and optional "Acquired by"
line), Sierra team member, stage (Seed / Series A/B/C = initial investment
round), status (Current / Exited), exit label (Exited / IPO), website and
sector labels.
Status: Current -> active; Exited -> acquired; IPO exits left blank (exit_type
keeps the raw label) since the site does not say acquired.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, stage_label, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.sierraventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "sierraventures_companies.json")
PRIMARY = "Sierra Ventures"
SECTOR_TAG_MAP = {
    "ai infrastructure": ["Dev Tools / Cloud"], "healthcare": ["Health"],
    "frontier tech": ["Deeptech / Robotics / AR/VR"], "security": ["Cybersecurity"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Altimate AI": ["Dev Tools / Cloud", "Data & Analytics"],
    "American Fiber Systems": ["Dev Tools / Cloud"],
    "AmorCode": ["Cybersecurity", "Dev Tools / Cloud"],
    "Applitools": ["Dev Tools / Cloud"],
    "Atmi": ["Deeptech / Robotics / AR/VR"],
    "Balto": ["Future of Work"],
    "CarWale": ["Transportation / Mobility", "Consumer"],
    "Centex": ["Dev Tools / Cloud"],
    "Citcon": ["FinTech / Insurance"],
    "Combinet": ["Dev Tools / Cloud"],
    "ConvergeNet": ["Dev Tools / Cloud"],
    "CSS Corp": ["Dev Tools / Cloud"],
    "DGiT": ["Gaming / Media / Entertainment"],
    "Fabric": ["Consumer", "Dev Tools / Cloud"],
    "FaxSav": ["Dev Tools / Cloud"],
    "Interact Commerce Corporation": ["Future of Work"],
    "Joy": ["Consumer"],
    "Mantle": ["FinTech / Insurance", "Future of Work"],
    "MeruNetworks": ["Dev Tools / Cloud"],
    "Modulate": ["Gaming / Media / Entertainment", "Cybersecurity"],
    "Pluto Health": ["Health", "Data & Analytics"],
    "ProductNow": ["Future of Work"],
    "Qeexo": ["Deeptech / Robotics / AR/VR"],
    "Quadratic 3D": ["Deeptech / Robotics / AR/VR"],
    "Quillbot": ["Future of Work"],
    "Runa": ["Consumer", "Data & Analytics"],
    "SalesLogix": ["Future of Work"],
    "Sedai": ["Dev Tools / Cloud"],
    "siena": ["Future of Work"],
    "SKSpruce": ["Dev Tools / Cloud"],
    "SupportLogic": ["Future of Work"],
    "Theta": ["Web3 / Crypto", "Gaming / Media / Entertainment"],
    "Thixel": ["Deeptech / Robotics / AR/VR"],
    "Vertel": ["Dev Tools / Cloud"],
    "Weav.ai": ["Future of Work"],
    "Wizeline": ["Dev Tools / Cloud"],
}


def field(obj, key):
    m = re.search(r'"%s":\s*"((?:[^"\\]|\\.)*)"' % key, obj)
    return clean(m.group(1)) if m else None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    start = html.index("arr_obj_portfolio")
    body = html[start:html.index("];", start)]
    objs = re.split(r'\n\s*\{\s*\n\s*"featured"', body)[1:]
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for o in objs:
        name = field(o, "name")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        m = re.search(r'"description":\s*`(.*?)`', o, re.S)
        desc = acquirer = None
        if m:
            s = BeautifulSoup(m.group(1), "html.parser")
            for h in s.select("h4"):
                h.decompose()
            paras = [clean(p.get_text(" ")) for p in s.select("p")] or [clean(s.get_text(" "))]
            paras = [p for p in paras if p]
            for p in list(paras):
                am = re.match(r"(?i)acquired by\s+(.+)", p)
                if am and len(p) < 80:
                    acquirer = clean(am.group(1).rstrip("."))
                    paras.remove(p)
            desc = " ".join(paras) or None
        tm_name = field(o, "team_member")
        if desc and re.match(r"(?i)team member:", desc):
            # the deal partner's "TEAM MEMBER: <name>" label leaks into some descriptions
            rest = re.sub(r"(?i)^team member:\s*", "", desc)
            if tm_name and rest.lower().startswith(tm_name.lower()):
                rest = rest[len(tm_name):]
            desc = clean(rest)
        st = re.search(r'"status":\s*\{"name":\s*"([^"]*)"', o)
        raw_status = clean(st.group(1)) if st else None
        exit_label = field(o, "acquired")
        sectors = re.findall(r'\{"name":\s*"([^"]+)",\s*"label"', o.split('"sector"', 1)[1]) if '"sector"' in o else []
        if (raw_status or "").lower() == "current":
            status = "active"
        elif (exit_label or "").upper() == "IPO":
            status = None  # exited via IPO: not an acquisition; raw kept in exit_type
        elif (raw_status or "").lower() == "exited" or (exit_label or "").lower() == "exited" or acquirer:
            status = "acquired"
        else:
            status = None
        out.append({
            "company_name": name,
            "description": desc,
            "tagline": field(o, "subtitle"),
            "company_url": clean_url(field(o, "website")),
            "status": status,
            "site_status": raw_status,
            "exit_type": exit_label,
            "acquirer": acquirer,
            "stage": stage_label(field(o, "stage")),
            "sectors": sectors,
            "partners": [field(o, "team_member")] if field(o, "team_member") else [],
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "stage", "acquirer", "sectors", "partners", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
