#!/usr/bin/env python3
"""360 Capital portfolio scraper -> threesixtycapital_companies.json
Source: https://www.360cap.vc/portfolio — Webflow CMS; each .w-dyn-item card has
a /portfolios/<slug> link plus .cms-portfolio-wrapper text (name, sector, HQ,
description, Exited/Current). Detail pages expose "Visit their website".
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.360cap.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "threesixtycapital_companies.json")
PRIMARY = "360 Capital"
SECTOR_TAG_MAP = {
    "climate tech": ["Climate / Sustainability"], "deep tech": ["Deeptech / Robotics / AR/VR"],
    "digital first": ["Dev Tools / Cloud"], "digital health": ["Health"], "fintech": ["FinTech / Insurance"],
    "saas": ["Dev Tools / Cloud"], "marketplace": ["Consumer"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for item in soup.select(".w-dyn-item"):
        a = item.select_one('a[href*="/portfolios/"]')
        card = item.select_one(".cms-portfolio-wrapper")
        if not card and not a:
            continue
        name = None
        img = (a.select_one("img[alt]") if a else None) or (card.select_one("img[alt]") if card else None)
        if img and img.get("alt"):
            name = clean(img.get("alt"))
        if not name and a and a.get("alt"):
            name = clean(a.get("alt"))
        txt = clean(card.get_text(" ")) if card else clean(item.get_text(" "))
        if not name and a and a.get("href"):
            slug = a["href"].rstrip("/").split("/")[-1]
            name = clean(slug.replace("-", " ").title())
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        status = None
        if txt:
            if re.search(r"\bExited\b", txt):
                status = "acquired"
            elif re.search(r"\bCurrent\b", txt):
                status = "active"
        desc = None
        m = re.search(
            r"(?:Switzerland|France|Italy|Germany|Spain|UK|United Kingdom|Belgium|Netherlands|Sweden|Israel|USA|United States|Europe|Ireland|Portugal|Austria|Denmark|Norway|Finland|Poland|Romania|Luxembourg)\s+(.+?)(?:\s+Exited|\s+Current|\s+[A-Z][a-z]+ \d{1,2}, \d{4}\s*$)",
            txt or "",
        )
        if m:
            desc = clean(m.group(1))
        sectors = []
        for lab in ("Climate Tech", "Deep Tech", "Digital First", "Digital Health", "Fintech", "SaaS", "Marketplace"):
            if lab.lower() in (txt or "").lower():
                sectors.append(lab)
        loc = None
        for country in ("Switzerland", "France", "Italy", "Germany", "Spain", "United Kingdom", "Belgium",
                        "Netherlands", "Sweden", "Israel", "United States", "Ireland", "Portugal", "Austria",
                        "Denmark", "Norway", "Finland", "Poland", "Romania", "Luxembourg", "UK", "USA", "Europe"):
            if re.search(r"\b" + re.escape(country) + r"\b", txt or ""):
                loc = country
                break
        detail = urljoin(SOURCE_URL, a["href"]) if a and a.get("href") else None
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": None,
            "sectors": sectors,
            "location": loc,
            "status": status,
            "detail_url": detail,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    pages = fetch_many([r["detail_url"] for r in out if r.get("detail_url")], workers=6, pause=0.15)
    for r in out:
        html = pages.get(r.get("detail_url"))
        if html:
            ds = BeautifulSoup(html, "html.parser")
            for a in ds.select("a[href^=http]"):
                label = (a.get_text(" ") or "").strip().lower()
                if "visit" in label and "website" in label:
                    r["company_url"] = clean_url(a["href"])
                    break
            if not r.get("description"):
                for p in ds.select("p"):
                    t = clean(p.get_text(" "))
                    if t and len(t) > 60:
                        r["description"] = t
                        break
            r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"), r.get("sectors"), SECTOR_TAG_MAP)
        r.pop("detail_url", None)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "status", "location", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
