#!/usr/bin/env python3
"""Point72 Ventures portfolio scraper -> point72ventures_companies.json
Source: https://p72.vc/portfolio/ — WP page, .c-portfolio__accordion rows (name,
sector, first-investment round, Founded / First invested / First investment /
Located in, description, website; data-active = the site's active-portfolio flag).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, stage_label, prune_substring_tags, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://p72.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "point72ventures_companies.json")
PRIMARY = "Point72 Ventures"
TAG_OVERRIDES = {  # judgment pass (no LLM)
    "Applied Labs": ["Future of Work"], "Apprente": ["Future of Work"], "Artificial Societies": ["Data & Analytics"],
    "Atomic Industries": ["Deeptech / Robotics / AR/VR"], "Boulevard": ["Consumer", "Future of Work"],
    "Docent": ["Consumer", "Gaming / Media / Entertainment"], "HANetf": ["FinTech / Insurance", "Web3 / Crypto"],
    "Knowde": ["Logistics / Supply Chain"], "Ladder": ["Consumer", "Health"], "Le Walk": ["Consumer", "Gaming / Media / Entertainment"],
    "LockStep": ["FinTech / Insurance"], "Metaphor": ["Data & Analytics"], "NEX": ["Gaming / Media / Entertainment"],
    "Nexad": ["Gaming / Media / Entertainment"], "PolyAI": ["Future of Work"], "Railbird": ["FinTech / Insurance"],
    "Spore.Bio": ["BioTech", "Health"], "Spuree": ["Gaming / Media / Entertainment"], "Stellar Health": ["Health"],
    "Tektonic": ["Future of Work"], "Tempo Automation": ["Deeptech / Robotics / AR/VR"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for acc in soup.select(".c-portfolio__accordion"):
        h3 = acc.select_one("h3")
        name = clean(h3.get_text(" ")) if h3 else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        facts = {}
        for h5 in acc.select("h5"):
            t = clean(h5.get_text(" ")) or ""
            m = re.match(r"(Founded|First invested|First investment):\s*(.+)", t)
            if m:
                facts[m.group(1)] = m.group(2)
            elif t.lower().startswith("located in"):
                facts["Located"] = clean(t[10:])
        sec = acc.select_one(".c-portfolio__disrupting span")
        content = acc.select_one(".c-portfolio__content")
        desc = clean(content.find("div").get_text(" ")) if content and content.find("div") else None
        a = content.select_one("a[href^=http]") if content else None
        first_round = facts.get("First investment") or (clean(acc.select_one(".c-portfolio__investment").get_text(" ")) if acc.select_one(".c-portfolio__investment") else None)
        yr = re.search(r"(19|20)\d\d", facts.get("First invested", ""))
        fy = re.search(r"(19|20)\d\d", facts.get("Founded", ""))
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a["href"]) if a else None,
            "sectors": [clean(sec.get_text(" "))] if sec and clean(sec.get_text(" ")) else [],
            "location": facts.get("Located"),
            "year_founded": int(fy.group(0)) if fy else None,
            "first_invested": int(yr.group(0)) if yr else None,
            "stage": stage_label(first_round) if first_round else None,
            "first_investment_raw": first_round,
            "status": "active" if acc.get("data-active") == "1" else None,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"], r["sectors"])
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "location", "stage", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
