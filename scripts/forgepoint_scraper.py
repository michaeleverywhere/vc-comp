#!/usr/bin/env python3
"""Forgepoint Capital portfolio scraper -> forgepoint_companies.json
Source: WP REST /wp-json/wp/v2/company + sector/status/location taxonomies.
Description scraped from public company detail pages when present.
"""
import os, sys, html as htmlmod
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, fetch_many
from _d20_common import write_out

SOURCE_URL = "https://forgepointcap.com/companies/"
REST = "https://www.forgepointcap.com/wp-json/wp/v2/company?per_page=100&page={}"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "forgepoint_companies.json")
PRIMARY = "Forgepoint Capital"
SECTOR_MAP = {
    "security operations": ["Cybersecurity"], "identity": ["Cybersecurity"],
    "cloud security": ["Cybersecurity"], "data security": ["Cybersecurity"],
    "application security": ["Cybersecurity"], "network security": ["Cybersecurity"],
    "threat intelligence": ["Cybersecurity"], "fraud": ["Cybersecurity", "FinTech / Insurance"],
}
TAG_OVERRIDES = {}


def tax_map(base, tax):
    url = f"{base}/wp-json/wp/v2/{tax}?per_page=100"
    try:
        items = fetch(url, as_json=True)
    except SystemExit:
        return {}
    return {c["id"]: clean(htmlmod.unescape(c["name"])) for c in items}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    base = "https://www.forgepointcap.com"
    sectors_map = tax_map(base, "sector")
    status_map = tax_map(base, "status")
    loc_map = tax_map(base, "location")
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
        sectors = [sectors_map[i] for i in p.get("sector", []) if i in sectors_map]
        statuses = [status_map[i] for i in (p.get("status") if isinstance(p.get("status"), list) else []) if i in status_map]
        # WP also encodes status in class_list
        cl = " ".join(p.get("class_list") or [])
        status = None
        if any("acquir" in s.lower() or s.lower() == "exited" for s in statuses) or "status-acquired" in cl or "status-exited" in cl:
            status = "acquired"
        elif any(s.lower() == "active" for s in statuses) or "status-active" in cl:
            status = "active"
        locs = [loc_map[i] for i in p.get("location", []) if i in loc_map]
        html = pages.get(p.get("link")) or ""
        soup = BeautifulSoup(html, "html.parser") if html else None
        desc = None
        website = None
        if soup:
            for sel in [".company-content p", ".entry-content p", "article p", ".company__description"]:
                for el in soup.select(sel):
                    t = clean(el.get_text(" "))
                    if t and len(t) > 30:
                        desc = t
                        break
                if desc:
                    break
            for a in soup.find_all("a", href=True):
                href = a["href"]
                label = (clean(a.get_text(" ")) or "").lower()
                if href.startswith("http") and "forgepoint" not in href and label in ("website", "visit", "company site", "visit website"):
                    website = clean_url(href)
                    break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": sectors,
            "location": locs[0] if locs else None,
            "status": status,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "sectors", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
