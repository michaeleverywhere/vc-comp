#!/usr/bin/env python3
"""Edison Partners portfolio scraper -> edison_companies.json
Source: https://www.edisonpartners.com/portfolio — HubSpot grid of a.portfolio__item
(logo alt name, industry / region / active|exited CSS classes) + detail pages
(Sector, Location, Date of Investment, description, "Go to company website").
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many, label_after, year_of,
                             prune_substring_tags, apply_tag_overrides, carry_forward_descriptions)
from _d20_common import write_out

SOURCE_URL = "https://www.edisonpartners.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "edison_companies.json")
PRIMARY = "Edison Partners"
SECTOR_TAG_MAP = {"financial technology": ["FinTech / Insurance"], "healthcare it": ["Health"],
                  "fintech": ["FinTech / Insurance"], "healthcare": ["Health"], "vertical saas & ai": [],
                  "enterprise solutions": []}
NAME_FIX = {"Mapppedin": "Mappedin"}  # site alt-text typo (company site: mappedin.com)
TAG_OVERRIDES = {  # judgment pass (no LLM)
    "120Water": ["Climate / Sustainability", "RegTech/Gov/Legal", "Data & Analytics"], "15Five": ["Future of Work"],
    "Anonos": ["Cybersecurity", "Data & Analytics"], "CleanDesign": ["Climate / Sustainability"], "ClearJet": ["Logistics / Supply Chain"],
    "Comply": ["RegTech/Gov/Legal", "FinTech / Insurance"], "Dash Solutions": ["FinTech / Insurance"],
    "DemandScience": ["Data & Analytics"], "Field Effect": ["Cybersecurity"], "Fingercheck": ["Future of Work", "FinTech / Insurance"],
    "GAN Integrity": ["RegTech/Gov/Legal"], "Havenly": ["Consumer", "PropTech"], "Health Recovery Solutions": ["Health"],
    "Houwzer": ["PropTech", "Consumer"], "Judi Health": ["Health", "FinTech / Insurance"], "Kaiyo": ["Consumer", "Climate / Sustainability"],
    "Lokavant": ["Health", "BioTech", "Data & Analytics"], "Mappedin": ["Data & Analytics", "Dev Tools / Cloud"],
    "Mediafly": ["Future of Work", "Data & Analytics"], "NPHub": ["Health"], "Overhaul": ["Logistics / Supply Chain"],
    "PurpleLab": ["Health", "Data & Analytics"], "Rapid Deploy": ["RegTech/Gov/Legal"], "Ringmaster Technologies": ["Health"],
    "RTS": ["Climate / Sustainability", "Logistics / Supply Chain"], "Seismos": ["Climate / Sustainability", "Data & Analytics"],
    "Slingshot Aerospace": ["Deeptech / Robotics / AR/VR", "Data & Analytics"], "Solutions by Text": ["FinTech / Insurance", "RegTech/Gov/Legal"],
    "TakeCommand": ["Health", "FinTech / Insurance"], "TripleLift": ["Gaming / Media / Entertainment"], "Upright": ["FinTech / Insurance", "PropTech"],
    "Vox Mobile": ["Dev Tools / Cloud"], "Zelis": ["Health", "FinTech / Insurance"], "Wyng": ["Gaming / Media / Entertainment"],
    "120water": ["Climate / Sustainability"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a.portfolio__item[href]"):
        img = a.select_one("img[alt]")
        name = clean(re.sub(r"(?i)\s*logo\s*$", "", img.get("alt") or "")) if img else None
        href = a["href"]
        if not name:
            name = clean(href.rstrip("/").split("/")[-1].replace("-", " ").title())
        name = NAME_FIX.get(name, name)
        if not name or href in seen:
            continue
        seen.add(href)
        cls = a.get("class") or []
        ind = a.select_one(".portfolio__industry")
        out.append({
            "company_name": name,
            "detail_url": href,
            "industry": clean(ind.get_text(" ")) if ind else None,
            "region": next((c.split("--", 1)[1].replace("-", " ").title() for c in cls if c.startswith("location--")), None),
            "site_status": "Exited" if "exited" in cls else ("Active" if "active" in cls else None),
        })
    pages = fetch_many([r["detail_url"] for r in out], workers=5, pause=0.15)
    for r in out:
        html = pages.get(r["detail_url"])
        desc = url = loc = sector = None
        yr = None
        if html:
            ds = BeautifulSoup(html, "html.parser")
            m = ds.select_one("main") or ds.body or ds
            strings = [clean(x) for x in m.stripped_strings]
            sector = label_after(strings, "Sector:", "Sector")
            loc = label_after(strings, "Location:", "Location")
            yr = year_of(label_after(strings, "Date of Investment:", "Date of Investment"))
            try:
                i = strings.index(next(s for s in strings if s and s.lower().startswith("date of investment")))
                cand = [s for s in strings[i + 2:i + 6] if s and len(s) > 60]
                desc = cand[0] if cand else None
            except StopIteration:
                pass
            go = next((x for x in m.select("a[href^=http]") if "company website" in x.get_text(" ").lower()), None)
            url = clean_url(go["href"]) if go else None
        st = (r["site_status"] or "").lower()
        r.update({
            "description": desc,
            "company_url": url,
            "sectors": [s for s in [sector or r.get("industry")] if s],
            "location": loc,
            "first_invested": yr,
            "status": "active" if st == "active" else None,
            "exited": st == "exited",
            "profile_url": r.pop("detail_url"),
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        r["everywhere_tags"] = tags_for(r["company_name"], desc, [r.get("industry")] + r["sectors"], SECTOR_TAG_MAP)
    for r in carry_forward_descriptions(out, OUT):
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"], [r.get("industry")] + r["sectors"], SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "location", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
