#!/usr/bin/env python3
"""Rampersand portfolio scraper -> rampersand_companies.json
Source: https://rampersand.vc/portfolio.html — the portfolio table is rendered from an
inline JS array (const COS = [...]) on the page: company, description, sector +
sector name, stage (funding round of Rampersand's entry), year (first invested),
move (Lead / Co-lead / Follow) and status (active / new / exit); website only where
the firm lists one."""
import os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://rampersand.vc/portfolio.html"
PRIMARY = "Rampersand"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "deeptech": ["Deeptech / Robotics / AR/VR"],
              "climate": ["Climate / Sustainability"], "health": ["Health"]}
STATUS = {"active": "active", "new": "active", "exit": "exited"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch_response(SOURCE_URL).content.decode("utf-8", "replace")
    i = html.find("const COS = [")
    if i < 0:
        raise SystemExit("FATAL: COS array not found")
    blob = html[i:html.find("];", i)]
    out = []
    for o in re.findall(r"\{\s*co:.*?\}", blob, re.S):
        f = {k: v for k, v in re.findall(r'(\w+)\s*:\s*"((?:[^"\\]|\\.)*)"', o)}
        f.update({k: int(v) for k, v in re.findall(r"(\w+)\s*:\s*(\d{4})\b", o)})
        name = clean(f.get("co"))
        if not name:
            continue
        site = clean(f.get("website"))
        st = (f.get("status") or "").lower()
        stage = clean(f.get("stage"))
        out.append(rec(name, clean(f.get("desc")), site if site and not is_social(site) else None, PRIMARY,
                       SOURCE_URL, scraped_at, sectors=[x for x in (f.get("sector"), f.get("sectorName")) if x],
                       sector_map=SECTOR_MAP, sector_name=clean(f.get("sectorName")),
                       stage=None if stage and "exit" in stage.lower() else stage,
                       first_invested=f.get("year") if isinstance(f.get("year"), int) else None,
                       rampersand_role=clean(f.get("move")), new_investment=(st == "new"),
                       exit_note=stage if stage and "exit" in stage.lower() else None,
                       status=STATUS.get(st, st or None)))
    finish(out, "rampersand", ("description", "stage", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
