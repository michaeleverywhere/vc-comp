#!/usr/bin/env python3
"""Basis Set Ventures portfolio scraper -> basisset_companies.json
Source: https://www.basisset.com/portfolio — Webflow. The list (rendered twice
on the page, deduped by URL) gives name, one-liner and BSV's category; each
/portfolio-companies/<slug> page adds Investment (round), Year, Location,
Founders, website and a long description. Stealth cards have no name and are
skipped.
"""
import json, os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, round_label, year_of, is_social

BASE = "https://www.basisset.com"
SOURCE_URL = BASE + "/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "basisset_companies.json")
PRIMARY = "Basis Set Ventures"
SECTOR_TAG_MAP = {
    "intelligent collaboration": ["Future of Work"], "fintech": ["FinTech / Insurance"],
    "healthcare": ["Health"], "health": ["Health"], "industrial automation": ["Deeptech / Robotics / AR/VR"],
    "robotics": ["Deeptech / Robotics / AR/VR"], "developer tools": ["Dev Tools / Cloud"],
    "infrastructure": ["Dev Tools / Cloud"], "security": ["Cybersecurity"], "consumer": ["Consumer"],
    "supply chain": ["Logistics / Supply Chain"], "logistics": ["Logistics / Supply Chain"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for it in soup.select(".portfolio-list_item"):
        a = it.select_one("a[href*='/portfolio-companies/']")
        nm = it.select_one(".company_name")
        name = clean(nm.get_text()) if nm else None
        if not a or not name:
            continue
        url = urljoin(BASE, a["href"])
        if url in seen:
            continue
        seen.add(url)
        d = it.select_one(".company_desc")
        c = it.select_one(".category")
        rows.append({"name": name, "profile": url, "blurb": clean(d.get_text(" ")) if d else None,
                     "category": clean(c.get_text()) if c else None})
    if limit:
        rows = rows[:limit]
    pages = fetch_many([r["profile"] for r in rows])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser")
        stats = {}
        for si in d.select(".portfolio-stat_item"):
            lab = si.select_one(".portfolio-stat_label")
            if not lab:
                continue
            key = clean(lab.get_text()).rstrip(":").lower()
            lab.extract()
            stats[key] = clean(si.get_text(" "))
        site = None
        for a in d.select("main a[href^='http'], a[href^='http']"):
            h = a["href"].strip()
            if "basisset" in h or "bsv.medium" in h or is_social(h) or "website-files" in h:
                continue
            site = h
            break
        # long description: the two paragraphs after the stat block
        paras = []
        sc = d.select_one(".portfolio-stat_container")
        if sc:
            for el in sc.find_all_next(["p", "div"], limit=40):
                if el.find(["p", "div"]):
                    continue
                t = clean(el.get_text(" "))
                if t and len(t) > 60 and t not in paras and not t.startswith("©"):
                    paras.append(t)
                if len(paras) >= 2:
                    break
        desc = paras[0] if paras else r["blurb"]
        founders = [clean(f) for f in (stats.get("founders") or "").split(";") if clean(f)]
        sectors = [r["category"]] if r["category"] else []
        out.append({
            "company_name": r["name"],
            "description": desc,
            "tagline": r["blurb"],
            "company_url": site,
            "company_profile_url": r["profile"],
            "status": None,
            "stage": round_label(stats.get("investment")),
            "investment_stage_raw": stats.get("investment"),
            "first_invested": year_of(stats.get("year")),
            "location": stats.get("location"),
            "founders": founders,
            "sectors": sectors,
            "everywhere_tags": tags_for(r["name"], " ".join(paras) or r["blurb"], sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "stage", "first_invested", "location", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
