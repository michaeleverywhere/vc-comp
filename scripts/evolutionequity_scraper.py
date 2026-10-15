#!/usr/bin/env python3
"""Evolution Equity Partners portfolio scraper -> evolutionequity_companies.json
Source: WP REST /wp-json/wp/v2/companies + theme/status_company/stage taxonomies.
"""
import os, sys, html as htmlmod
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, fetch_many, stage_label
from _d20_common import write_out

SOURCE_URL = "https://evolutionequity.com/portfolio/"
REST = "https://evolutionequity.com/wp-json/wp/v2/companies?per_page=100&page={}"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "evolutionequity_companies.json")
PRIMARY = "Evolution Equity Partners"
SECTOR_MAP = {
    "cybersecurity": ["Cybersecurity"], "security": ["Cybersecurity"],
    "ai software development": ["Dev Tools / Cloud"], "enterprise software": [],
    "data": ["Data & Analytics"], "cloud": ["Dev Tools / Cloud"],
}
TAG_OVERRIDES = {}


def tax_map(tax):
    try:
        items = fetch(f"https://evolutionequity.com/wp-json/wp/v2/{tax}?per_page=100", as_json=True)
    except SystemExit:
        return {}
    return {c["id"]: clean(htmlmod.unescape(c["name"])) for c in items}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    themes = tax_map("theme")
    statuses = tax_map("status_company")
    stages = tax_map("stage")
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
        sectors = [themes[i] for i in p.get("theme", []) if i in themes]
        st_list = [statuses[i] for i in p.get("status_company", []) if i in statuses]
        stage_list = [stages[i] for i in p.get("stage", []) if i in stages]
        status = None
        if any("acquir" in s.lower() or s.lower() == "exited" for s in st_list):
            status = "acquired"
        elif any(s.lower() == "active" for s in st_list):
            status = "active"
        # stage taxonomy may be "Growth"/"Early" — only keep real funding rounds
        stage = None
        for s in stage_list:
            sl = stage_label(s)
            if sl:
                stage = sl
                break
        html = pages.get(p.get("link")) or ""
        soup = BeautifulSoup(html, "html.parser") if html else None
        desc = website = None
        if soup:
            for el in soup.select("article p, .entry-content p, .company-content p"):
                t = clean(el.get_text(" "))
                if t and len(t) > 30:
                    desc = t
                    break
            for a in soup.find_all("a", href=True):
                href = a["href"]
                label = (clean(a.get_text(" ")) or "").lower()
                if href.startswith("http") and "evolutionequity" not in href and label in ("website", "visit website", "company website"):
                    website = clean_url(href)
                    break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": sectors,
            "stage": stage,
            "status": status,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "sectors", "stage", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
