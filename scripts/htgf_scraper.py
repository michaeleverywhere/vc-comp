#!/usr/bin/env python3
"""High-Tech Gründerfonds (HTGF) portfolio scraper -> htgf_companies.json
Source: https://www.htgf.de/en/portfolio/ — WordPress. The full English portfolio
list comes from the public WP REST endpoint /wp-json/wp/v2/portfolio?lang=en
(title, link, class_list sector/focus-area slugs, Yoast meta description). Each
detail page (/en/portfolio/htgffamily/<slug>/) adds a Key Facts table
("Invested since" YYYY, "Based in" city), the "About the company" text and the
company website button. Exited companies carry an "(Exit)" suffix in their
title: stripped from the name and kept as site_status "Exit" (HTGF does not say
acquired, so no lead status). Header labels that are German states or
"International" go to region, the rest to sectors. first_invested = "Invested since" year. Sector labels
are HTGF's own (Digital Tech / Industrial Tech / Life Sciences / ... and focus
areas). No round or status published.
"""
import html as htmlmod, json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch_response, fetch_many, clean, tags_for, clean_url, year_of,
                             prune_substring_tags, apply_tag_overrides, is_social)
from _d20_common import write_out

SOURCE_URL = "https://www.htgf.de/en/portfolio/"
API = "https://www.htgf.de/wp-json/wp/v2/portfolio?lang=en&per_page=100&page={}"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "htgf_companies.json")
PRIMARY = "High-Tech Gründerfonds"
SECTOR_TAG_MAP = {
    "life sciences": ["BioTech"], "biotech": ["BioTech"], "medtech": ["Health"], "digital health": ["Health"],
    "pharma": ["BioTech"], "diagnostics": ["Health"], "cyber security": ["Cybersecurity"],
    "fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"], "agritech": ["Climate / Sustainability"],
    "food": ["CPG"], "cleantech": ["Climate / Sustainability"], "energy": ["Climate / Sustainability"],
    "climate tech": ["Climate / Sustainability"], "mobility": ["Transportation / Mobility"],
    "robotics": ["Deeptech / Robotics / AR/VR"], "quantum": ["Deeptech / Robotics / AR/VR"],
    "photonics": ["Deeptech / Robotics / AR/VR"], "semiconductors": ["Deeptech / Robotics / AR/VR"],
    "space tech": ["Deeptech / Robotics / AR/VR"], "logistics": ["Logistics / Supply Chain"],
    "proptech": ["PropTech"], "construction tech": ["PropTech"], "gaming": ["Gaming / Media / Entertainment"],
    "media": ["Gaming / Media / Entertainment"], "hr tech": ["Future of Work"], "edtech": ["Future of Work"],
    "legal tech": ["RegTech/Gov/Legal"], "blockchain": ["Web3 / Crypto"], "data analytics": ["Data & Analytics"],
}
SKIP_LABELS = {"international", "digital tech", "industrial tech", "chemistry & materials", "life sciences & chemistry"}
REGION_LABELS = {"international", "baden-württemberg", "bavaria", "berlin", "brandenburg", "bremen", "hamburg",
                 "hesse", "lower saxony", "mecklenburg-western pomerania", "north rhine-westphalia",
                 "rhineland-palatinate", "saarland", "saxony", "saxony-anhalt", "schleswig-holstein", "thuringia"}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "Samp": ["Deeptech / Robotics / AR/VR"],
    "faCellitate": ["BioTech"],
    "Threedy": ["Deeptech / Robotics / AR/VR", "Dev Tools / Cloud"],
    "DIMATE": ["Dev Tools / Cloud"],
    "memetis": ["Deeptech / Robotics / AR/VR"],
    "NYRIS": ["Data & Analytics", "Deeptech / Robotics / AR/VR"],
    "Volterion": ["Climate / Sustainability"],
    "Selfapy": ["Health"],
    "MoBerries": ["Future of Work"],
    "Semknox": ["Consumer"],
    "fodjan": ["Climate / Sustainability", "Data & Analytics"],
    "Lockbox": ["Logistics / Supply Chain", "Consumer"],
    "LEDexchange": ["Climate / Sustainability"],
    "Terrawater": ["Climate / Sustainability"],
    "Product Value Systems": ["Data & Analytics"],
    "VisuMotion": ["Deeptech / Robotics / AR/VR"],
    "windeln.de": ["Consumer"],
    "4 Animals AlsterScience": ["BioTech"],
    "givve": ["FinTech / Insurance"],
    "Tixel": ["Dev Tools / Cloud"],
    "softgarden": ["Future of Work"],
    "Semasio": ["Gaming / Media / Entertainment", "Data & Analytics"],
    "Notion Systems": ["Deeptech / Robotics / AR/VR"],
    "Next Kraftwerke": ["Climate / Sustainability"],
    "Middle Peak": ["Health"],
    "m2p-labs": ["BioTech"],
    "Limata": ["Deeptech / Robotics / AR/VR"],
    "HQ plus": ["Data & Analytics"],
    "futalis": ["CPG"],
    "FIDLOCK": ["Deeptech / Robotics / AR/VR"],
    "CCI Custom Cells Itzehoe": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Cuciniale": ["Consumer"],
    "Confovis": ["Deeptech / Robotics / AR/VR"],
    "EH-D": ["Deeptech / Robotics / AR/VR"],
}


def slug_label(s):
    return s.replace("-", " ").strip()


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    items, page = [], 1
    while True:
        r = fetch_response(API.format(page))
        batch = r.json()
        items += batch
        if page >= int(r.headers.get("X-WP-TotalPages", "1")) or not batch:
            break
        page += 1
    pages = fetch_many([x["link"] for x in items], workers=8)
    out, seen = [], set()
    for x in items:
        name = clean(htmlmod.unescape(x["title"]["rendered"]))
        exited = bool(name and re.search(r"\(\s*exit\s*\)\s*$", name, re.I))
        name = clean(re.sub(r"\(\s*exit\s*\)\s*$", "", name or "", flags=re.I))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        meta_desc = clean(((x.get("yoast_head_json") or {}).get("description")) or "")
        desc = site = loc = None
        since = None
        labels = []
        html = pages.get(x["link"])
        if html:
            s = BeautifulSoup(html, "html.parser")
            for tr in s.select("#key-facts tr"):
                tds = [clean(td.get_text(" ")) for td in tr.select("td")]
                if len(tds) == 2:
                    if (tds[0] or "").lower().startswith("invested since"):
                        since = year_of(tds[1])
                    elif (tds[0] or "").lower().startswith("based in"):
                        loc = tds[1]
            head = s.select_one("#main-info-desktop")
            if head:
                labels = [clean(a.get_text(" ")) for a in head.select(".wp-block-button__link") if clean(a.get_text(" "))]
            info = s.select_one("#company-info")
            if info:
                paras = [clean(p.get_text(" ")) for p in info.select("p") if clean(p.get_text(" "))]
                desc = " ".join(paras) or None
                for a in info.select("a[href^=http]"):
                    h = a["href"]
                    if "htgf.de" not in h and not is_social(h):
                        site = clean_url(h)
                        break
        if not labels:
            labels = [slug_label(c.split("-", 1)[1]) for c in x.get("class_list", [])
                      if c.startswith(("sectors-", "focus_areas-"))]
        region = [l for l in labels if l.lower() in REGION_LABELS]
        sectors = [l for l in labels if l.lower() not in REGION_LABELS]
        desc = desc or meta_desc
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": site,
            "sectors": sectors,
            "location": loc,
            "first_invested": since,
            "region": ", ".join(region) or None,
            "site_status": "Exit" if exited else None,
            "everywhere_tags": tags_for(name, desc, [l for l in sectors if l.lower() not in SKIP_LABELS], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": x["link"],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "location", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
