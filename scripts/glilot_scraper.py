#!/usr/bin/env python3
"""Glilot Capital portfolio scraper -> glilot_companies.json
Source: WP REST /wp-json/wp/v2/clubs (portfolio companies) + clubs-category.
"""
import os, sys, html as htmlmod
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, fetch_many
from _d20_common import write_out

SOURCE_URL = "https://www.glilotcapital.com/portfolio"
REST = "https://www.glilotcapital.com/wp-json/wp/v2/clubs?per_page=100&page={}"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "glilot_companies.json")
PRIMARY = "Glilot Capital"
SECTOR_MAP = {
    "cybersecurity": ["Cybersecurity"], "security": ["Cybersecurity"],
    "fintech": ["FinTech / Insurance"], "enterprise": [],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    try:
        cats = {c["id"]: clean(htmlmod.unescape(c["name"])) for c in fetch(
            "https://www.glilotcapital.com/wp-json/wp/v2/clubs-category?per_page=100", as_json=True)}
    except SystemExit:
        cats = {}
    posts, page = [], 1
    while True:
        batch = fetch(REST.format(page), as_json=True)
        if not batch:
            break
        posts += batch
        if len(batch) < 100:
            break
        page += 1
    pages = fetch_many([p.get("link") for p in posts if p.get("link")], workers=6, pause=0.15)
    out, seen = [], set()
    for p in posts:
        name = clean(htmlmod.unescape(p["title"]["rendered"]))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        sectors = [cats[i] for i in p.get("clubs-category", []) if i in cats]
        html = pages.get(p.get("link")) or ""
        soup = BeautifulSoup(html, "html.parser") if html else None
        desc = website = None
        if soup:
            for el in soup.select("article p, .entry-content p, .elementor-widget-container p"):
                t = clean(el.get_text(" "))
                if t and len(t) > 40 and "glilot" not in t.lower():
                    desc = t
                    break
            for a in soup.find_all("a", href=True):
                href = a["href"]
                label = (clean(a.get_text(" ")) or "").lower()
                if href.startswith("http") and "glilot" not in href and label in ("website", "visit website", "company website", "visit"):
                    website = clean_url(href)
                    break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
