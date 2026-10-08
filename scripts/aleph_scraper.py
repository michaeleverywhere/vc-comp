#!/usr/bin/env python3
"""Aleph portfolio scraper -> aleph_companies.json
Source: https://www.aleph.vc/companies — Webflow CMS grid, server-rendered.
Each card: name, founders (name + title), description, an exit pill
("Acquired by ..." / "IPO: ... NYSE: ...") and hidden list-js data
(category, vertical, year = Aleph's investment year, is_eu). Each
/companies/<slug> detail page adds the company website and "Entry Round"
(Aleph's entry funding round; first round listed -> stage). The
vertical label is kept in sectors but not used for tagging (it is often
mislabelled on the site, e.g. Houseparty = Logistics). No HQ location is published.
Status: "Acquired by X" pill -> acquired (acquirer kept); IPO pills are kept
raw in exit_detail with status blank; no pill -> status blank (the site does
not label live companies).
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, label_after, first_external_link, clean_url, stage_label, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.aleph.vc/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "aleph_companies.json")
PRIMARY = "Aleph"
OWN = ("aleph.vc", "website-files.com", "webflow")
SECTOR_TAG_MAP = {
    "financial services": ["FinTech / Insurance"], "healthcare": ["Health"], "deep tech": ["Deeptech / Robotics / AR/VR"],
    "consumer internet": ["Consumer"], "hr": ["Future of Work"], "legal": ["RegTech/Gov/Legal"],
    "data infrastructure": ["Data & Analytics", "Dev Tools / Cloud"], "developer tools": ["Dev Tools / Cloud"],
    "automotive": ["Transportation / Mobility"], "real estate": ["PropTech"], "education": ["Future of Work"],
    "travel": ["Consumer"], "web3": ["Web3 / Crypto"], "cyber security": ["Cybersecurity"],
    "logistics": ["Logistics / Supply Chain"], "insurance": ["FinTech / Insurance"], "gaming": ["Gaming / Media / Entertainment"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Empathy": ["Consumer", "RegTech/Gov/Legal"],
    "Luminate": ["Data & Analytics"],
    "Ply": ["Future of Work", "Dev Tools / Cloud"],
    "Raftt": ["Dev Tools / Cloud"],
    "Svix": ["Dev Tools / Cloud"],
    "Umbrella": ["Data & Analytics"],
    "Windward": ["Logistics / Supply Chain", "Data & Analytics"],
    "Workiz": ["Future of Work"],
}


def entry_stage(raw):
    """Aleph's entry round = first round listed ("Seed, Round A" -> Seed;
    "Round B" -> Series B; "A" -> Series A). Founders / Early Stage -> None."""
    first = clean((raw or "").split(",")[0])
    if not first:
        return None
    m = re.fullmatch(r"(?i)(?:round|series)?\s*([a-h])", first)
    if m:
        return "Series " + m.group(1).upper()
    return stage_label(first)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards, seen = [], set()
    for it in soup.select(".company_item"):
        data = {d.get("data-filter"): clean(d.get_text(" ")) for d in it.select(".list-js-data [data-filter]")}
        name = data.get("name")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        a = it.select_one("a.cover-link[href]")
        d = it.select_one(".company_description")
        founders = []
        for f in it.select(".company_item-name-wrap"):
            sp = [clean(x.get_text(" ")) for x in f.select(".company_name")]
            if sp and sp[0]:
                founders.append(sp[0])
        pill = it.select_one(".pill-company")
        cards.append(dict(name=name, prof=urljoin(SOURCE_URL, a["href"]) if a else None,
                          desc=clean(d.get_text(" ")) if d else None, founders=founders,
                          pill=clean(pill.get_text(" ")) if pill else None, data=data))
        if limit and len(cards) >= limit:
            break
    details = fetch_many([c["prof"] for c in cards if c["prof"]])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for c in cards:
        site = entry = None
        h = details.get(c["prof"])
        if h:
            s = BeautifulSoup(h, "html.parser")
            site = clean_url(first_external_link(s, OWN))
            entry = label_after(s.stripped_strings, "Entry Round")
        pill = c["pill"]
        acq = re.match(r"(?i)acquired by\s+(.+)", pill or "")
        cat, vert, year = c["data"].get("category"), c["data"].get("vertical"), c["data"].get("year")
        sectors = [x for x in (cat, vert) if x]
        desc = (c["desc"] or "").strip('"').strip() or None
        out.append({
            "company_name": c["name"],
            "description": desc,
            "company_url": site,
            "company_profile_url": c["prof"],
            "status": "acquired" if acq else None,
            "exit_detail": pill,
            "acquirer": clean(acq.group(1)) if acq else None,
            "stage": entry_stage(entry),
            "entry_round": entry,
            "first_invested": int(year) if year and re.fullmatch(r"\d{4}", year) else None,
            "founders": c["founders"],
            "sectors": sectors,
            "everywhere_tags": tags_for(c["name"], desc, [cat] if cat else [], SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "stage", "first_invested", "founders", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
