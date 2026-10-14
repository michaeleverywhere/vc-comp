#!/usr/bin/env python3
"""OCA Ventures portfolio scraper -> ocaventures_companies.json
Source: https://www.ocaventures.com/portfolio — SSR logo cards (.card-reveal):
name, one-line description, "Partnered since <round|year>", "Acquired by X YYYY",
sector, HQ location, website.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, stage_label, prune_substring_tags, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.ocaventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "ocaventures_companies.json")
PRIMARY = "OCA Ventures"
SECTOR_TAG_MAP = {
    "enterprise software": [],
    "digital health": ["Health"],
    "entrerprise software & digital health": ["Health"],
    "enterprise software & digital health": ["Health"],
    "fintech": ["FinTech / Insurance"],
    "fintech & digital health": ["FinTech / Insurance", "Health"],
    "medtech/biotech": ["Health", "BioTech"],
    "consumer software": ["Consumer"],
}
TAG_OVERRIDES = {  # judgment pass (no LLM)
    "AI Responsibility Lab": ["Dev Tools / Cloud"],
    "Alembic": ["Data & Analytics"],
    "Curate": [],
    "Genvid": ["Gaming / Media / Entertainment"],
    "Livly": ["PropTech"],
    "Placer.ai": ["Data & Analytics"],
    "Preflight": ["Dev Tools / Cloud"],
    "UBIQ": ["Cybersecurity", "Dev Tools / Cloud"],
    "Spider Oak": ["Cybersecurity"],
    "Roq.ad": ["Data & Analytics"],
    "Snapsheet": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "BUDDY": ["FinTech / Insurance"],
    "Falcon": ["FinTech / Insurance"],
    "Kraken Ventures": ["Web3 / Crypto"],
    "Spot Hero": ["Transportation / Mobility", "Consumer"],
    "Hubly": ["FinTech / Insurance"],
    "The Mom Project": ["Future of Work"],
    "Crafty": ["Future of Work"],
}


def entry_stage(raw):
    s = clean(raw) or ""
    if re.search(r"(?i)pre[- ]?(series )?seed", s):
        return "Pre-Seed"
    return stage_label(s)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for cd in soup.select("div.card-reveal"):
        nm = cd.select_one("div[class*=Typography]")
        name = clean(nm.get_text(" ")) if nm else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        h3 = cd.select_one("h3")
        desc = clean(h3.get_text(" ")) if h3 else None
        parts = []
        for sp in cd.select(".RichEditor-unstyled span[data-offset-key]"):
            for line in sp.get_text().split("\n"):
                if clean(line):
                    parts.append(clean(line))
        partnered = next((p for p in parts if p.lower().startswith("partnered since")), None)
        acq = next((p for p in parts if p.lower().startswith("acquired by")), None)
        rest = [p for p in parts if p not in (partnered, acq)]
        if not desc and rest and len(rest[0]) > 40:
            desc = rest.pop(0)
        sector = rest[0] if rest else None
        location = rest[1] if len(rest) > 1 else None
        raw_since = re.sub(r"(?i)^partnered since\s*", "", partnered or "").strip() or None
        a = cd.parent.select_one("a[href^=http]") if cd.parent else None
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a["href"]) if a else None,
            "sectors": [sector] if sector else [],
            "location": location,
            "stage": entry_stage(raw_since) if raw_since else None,
            "first_partnered_raw": raw_since,
            "first_invested": int(raw_since) if raw_since and re.fullmatch(r"(19|20)\d\d", raw_since) else None,
            "status": "acquired" if acq else None,
            "acquirer": None,
            "exit_year": None,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        if acq:
            m = re.match(r"(?i)acquired by\s+(.*?)\s*((?:19|20)\d\d)?\s*$", acq)
            if m:
                rec["acquirer"] = clean(m.group(1))
                rec["exit_year"] = int(m.group(2)) if m.group(2) else None
        rec["everywhere_tags"] = tags_for(name, desc, rec["sectors"], SECTOR_TAG_MAP)
        out.append(rec)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "location", "stage", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
