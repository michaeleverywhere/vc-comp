#!/usr/bin/env python3
"""Viola Group portfolio scraper -> viola_companies.json
Source: https://www.viola-group.com/portfolio/ — WordPress; the grid is
loaded from the site's own JSON endpoint /api/portfolio-filter.php (list:
title, Active / Exit, funding Viola arm(s) — Viola Ventures / Growth /
Fintech / Credit — Viola partner, industry), and each popup from the same
endpoint with ?id=<post id> (description, website). No stage, HQ or
investment year is published.
Status: Active -> active; Exit -> acquired only when the description says
the company was acquired (Viola marks fund exits such as IPOs / secondary
sales as "Exit" too, e.g. Payoneer, Redis); raw label kept in site_status.
"""
import html as htmlmod, json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, html_text, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.viola-group.com/portfolio/"
API = "https://www.viola-group.com/api/portfolio-filter.php"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "viola_companies.json")
PRIMARY = "Viola Group"
SECTOR_TAG_MAP = {
    "ai infra": ["Dev Tools / Cloud"], "climatech": ["Climate / Sustainability"],
    "construction & proptech": ["PropTech"], "consumer & gaming": ["Consumer", "Gaming / Media / Entertainment"],
    "content & media": ["Gaming / Media / Entertainment"], "creator economy": ["Gaming / Media / Entertainment"],
    "cyber": ["Cybersecurity"], "data & cloud infrastructure": ["Dev Tools / Cloud", "Data & Analytics"],
    "defensetech": ["RegTech/Gov/Legal"], "fintech": ["FinTech / Insurance"], "healthcare": ["Health"],
    "insurtech": ["FinTech / Insurance"], "marketing & bi": ["Data & Analytics"], "quantum": ["Deeptech / Robotics / AR/VR"],
    "retailtech": ["Consumer"], "semiconductors": ["Deeptech / Robotics / AR/VR"], "traveltech": ["Consumer"],
    "web3": ["Web3 / Crypto"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Aeronautics": ["Deeptech / Robotics / AR/VR"],
    "ALVIERE": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "Clarizen": ["Future of Work"],
    "Faddom": ["Dev Tools / Cloud"],
    "Global Data Center": ["Dev Tools / Cloud"],
    "Grover": ["Consumer"],
    "Guesty": ["PropTech", "Consumer"],
    "Impala AI": ["Dev Tools / Cloud"],
    "Lin health": ["Health"],
    "LiveU": ["Gaming / Media / Entertainment", "Dev Tools / Cloud"],
    "Oversi": ["Gaming / Media / Entertainment", "Dev Tools / Cloud"],
    "pagaya": ["FinTech / Insurance"],
    "PandoLogic": ["Future of Work"],
    "Proteantecs": ["Deeptech / Robotics / AR/VR", "Data & Analytics"],
    "Redis": ["Dev Tools / Cloud", "Data & Analytics"],
    "rr media": ["Gaming / Media / Entertainment"],
    "Samanage": ["Dev Tools / Cloud", "Future of Work"],
    "Scopio": ["Health"],
    "SnapTu Ltd. / Facebook": ["Consumer"],
    "Verbit": ["Future of Work"],
    "Vimi": ["Consumer"],
    "Worthy": ["Consumer"],
    "Zoomin": ["Data & Analytics"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    rows = fetch(f"{API}?activeexit=&industry=&fund=&search=&per_page=1000&page=1", as_json=True)
    if limit:
        rows = rows[:limit]
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for r in rows:
        name = clean(htmlmod.unescape(r.get("title") or ""))
        pub = clean(htmlmod.unescape(r.get("public_name") or ""))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        d = fetch(f"{API}?id={r['id']}", as_json=True)
        content = d.get("content") or ""
        paras = [clean(htmlmod.unescape(html_text(p) or "")) for p in re.split(r"\r?\n\s*\r?\n", content)]
        paras = [p for p in paras if p]
        desc = " ".join(paras[:2]) or None
        raw = clean(r.get("activeexit"))
        acq = re.search(r"(?i)\bacquired by ([A-Z][\w&.\- ]+?)(?: in | for |[.,(]|$)", content) or \
            re.search(r"(?i)\bwas acquired\b", content)
        if (raw or "").lower() == "active":
            status = "active"
        elif (raw or "").lower() == "exit" and acq:
            status = "acquired"
        else:
            status = None
        industries = [clean(i.get("name")) for i in r.get("industry") or [] if clean(i.get("name"))]
        funds = [clean(f.get("name")) for f in r.get("related_funds") or [] if clean(f.get("name"))]
        partners = [clean(f.get("name")) for f in r.get("funded_by") or [] if clean(f.get("name"))]
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(d.get("website")),
            "status": status,
            "site_status": raw,
            "acquirer": clean(acq.group(1)) if acq and acq.groups() else None,
            # for exits Viola shows the acquirer / listing (e.g. "Microsoft", "TASE:ITMR") as the public name
            "exit_detail": pub if raw == "Exit" and pub and pub.lower() != name.lower() else None,
            "sectors": industries,
            "funds": funds,
            "partners": partners,
            "everywhere_tags": tags_for(name, desc, industries, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "acquirer", "sectors", "funds", "partners", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
