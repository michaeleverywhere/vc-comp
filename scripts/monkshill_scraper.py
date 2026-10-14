#!/usr/bin/env python3
"""Monk's Hill Ventures portfolio scraper -> monkshill_companies.json
Source: https://www.monkshill.com/portfolio (Webflow CMS grid: sector label,
acquired/exited badge) plus each /portfolio/<slug> page's <title>
("MHV Portfolio: <Name> - <Sector>") and meta description.
Websites are not published on the pages.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, prune_substring_tags, apply_tag_overrides, carry_forward_descriptions
from _d20_common import write_out

SOURCE_URL = "https://www.monkshill.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "monkshill_companies.json")
PRIMARY = "Monk's Hill Ventures"
SECTOR_MAP = {
    "fintech": ["FinTech / Insurance"],
    "insurtech": ["FinTech / Insurance"],
    "healthtech": ["Health"],
    "edtech": ["Future of Work"],
    "hr tech": ["Future of Work"],
    "collaboration": ["Future of Work"],
    "logistics": ["Logistics / Supply Chain"],
    "e-commerce": ["Consumer"],
    "c2b e-commerce": ["Consumer", "Transportation / Mobility"],
    "prop tech": ["PropTech"],
    "proptech": ["PropTech"],
    "robotics": ["Deeptech / Robotics / AR/VR"],
    "clean tech": ["Climate / Sustainability"],
    "solar homes": ["Climate / Sustainability", "PropTech"],
    "circular economy": ["Climate / Sustainability", "Consumer"],
    "aquaculture tech": ["Climate / Sustainability"],
    "travel tech": ["Consumer"],
}
TAG_OVERRIDES = {
    "Radiant1": ["Data & Analytics"],
    "UIlicious": ["Dev Tools / Cloud"],
    "Ninja Van": ["Logistics / Supply Chain"],
    "NOVI Health": ["Health"],
    "twoplus Fertility": ["Health"],
    "Cinch": ["Consumer", "Climate / Sustainability"],
    "Saladin": ["FinTech / Insurance"],
    "Jenfi": ["FinTech / Insurance"],
    "Openexus": ["PropTech"],
    "Bot MD": ["Health"],
    "Acme": ["FinTech / Insurance"],
    "Tigerhall": ["Future of Work"],
    "Blue Whale Energy": ["Climate / Sustainability"],
    "Stellar": ["FinTech / Insurance"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    items = []
    for it in soup.select(".w-dyn-item"):
        a = it.select_one('a.know-more[href^="/portfolio/"]')
        if not a:
            continue
        badge = it.select_one(".acquired-exited")
        label = None
        if badge and "w-condition-invisible" not in (badge.get("class") or []):
            label = clean(badge.get_text(" ", strip=True))
        sec = it.select_one(".h5")
        items.append((urljoin(SOURCE_URL, a["href"]), clean(sec.get_text()) if sec else None, label))
    pages = fetch_many([u for u, _, _ in items], workers=4)
    out, seen = [], set()
    for url, sector, label in items:
        html = pages.get(url) or ""
        d = BeautifulSoup(html, "html.parser")
        title = clean(d.title.get_text()) if d.title else None
        name = None
        if title:
            m = re.match(r"MHV Portfolio:\s*(.+)$", title)
            name = clean(m.group(1)) if m else None
            if name and sector and name.lower().endswith((" - " + sector).lower()):
                name = clean(name[: -len(sector) - 3])
        if not name:
            name = url.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title()
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        md = d.select_one('meta[name="description"]') or d.select_one('meta[property="og:description"]')
        desc = clean(md.get("content")) if md else None
        low = (label or "").lower()
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": None,
            "sectors": [sector] if sector else [],
            "exit_detail": label,
            "status": "acquired" if "acquired" in low else None,
            "exited": bool(label),
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": url,
            "scraped_at": scraped_at,
        })
    carry_forward_descriptions(out, OUT)
    for r in out:
        mapped = SECTOR_MAP.get((r["sectors"] or [""])[0].lower(), [])
        kw = [t for t in tags_for(r["company_name"], r["description"]) if t not in mapped]
        r["everywhere_tags"] = (mapped + kw)[:3]
    prune_substring_tags(out, SECTOR_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
