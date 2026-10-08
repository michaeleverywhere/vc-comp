#!/usr/bin/env python3
"""Vsquared Ventures portfolio scraper -> vsquared_companies.json
Source: https://vsquared.vc/portfolio/ — WordPress + Search & Filter Pro. All
cards render server-side: company name (h4), uppercase tagline, and the card
link is the company website. "Generational Growth Themes" are a taxonomy
(_sft_typification); each theme's filtered results page is fetched to attach
the theme(s) as sectors. No status, round, year or location is published.
"""
import json, os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://vsquared.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "vsquared_companies.json")
PRIMARY = "Vsquared Ventures"
SECTOR_TAG_MAP = {
    "energy transition": ["Climate / Sustainability"], "new computing & sensing": ["Deeptech / Robotics / AR/VR"],
    "new space": ["Deeptech / Robotics / AR/VR"], "robotics & manufacturing": ["Deeptech / Robotics / AR/VR"],
    "tech-bio": ["BioTech"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Hyperganic": ["Deeptech / Robotics / AR/VR"],
    "Safe Intelligence": ["Dev Tools / Cloud"],
    "Sidos": ["Deeptech / Robotics / AR/VR"],
    "Zama": ["Cybersecurity"],
}


def cards(html):
    soup = BeautifulSoup(html, "html.parser")
    for c in soup.select(".portfolio__card__detailed"):
        h = c.select_one(".portfolio__back--title")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if name:
            yield name, c, soup


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    themes = {o["value"]: clean(o.get_text()) for o in soup.select('select[name="_sft_typification[]"] option') if o.get("value")}
    theme_of = {}
    for slug, label in themes.items():
        for name, _, _ in cards(fetch(f"{SOURCE_URL}?_sft_typification={slug}")):
            theme_of.setdefault(name.lower(), []).append(label)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for name, c, _ in cards(html):
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        tag = c.select_one("p.portfolio__back--name")
        tagline = clean(tag.get_text(" ", strip=True)) if tag else None
        if tagline and tagline.isupper():
            tagline = tagline[0] + tagline[1:].lower()
        a = c.select_one("a.portfolio__back[href]")
        sectors = theme_of.get(name.lower(), [])
        out.append({
            "company_name": name,
            "description": tagline,
            "tagline": tagline,
            "company_url": clean_url(a["href"]) if a else None,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, tagline, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
