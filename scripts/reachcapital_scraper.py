#!/usr/bin/env python3
"""Reach Capital portfolio scraper -> reachcapital_companies.json
Source: WP REST https://reachcapital.com/wp-json/wp/v2/portfolio + companies HTML cards for blurbs.
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone
from html import unescape

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_response, clean, html_text

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

API = "https://reachcapital.com/wp-json/wp/v2/portfolio"
COMPANIES_URL = "https://reachcapital.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "reachcapital_companies.json")
PRIMARY = "Reach Capital"

SECTOR_MAP = {374: "AI", 9: "Health", 10: "Learning", 8: "Work"}
STATUS_MAP = {3: "Active", 4: "Exit", 5: "Partial Exit", 2: "Pre-Seed"}
SECTOR_TAGS = {
    "AI": ["Deeptech / Robotics / AR/VR", "Dev Tools / Cloud"],
    "Health": ["Health"],
    "Learning": ["Future of Work", "Consumer"],
    "Work": ["Future of Work"],
}


def load_html_cards():
    """Optional blurbs from the public companies page cards."""
    try:
        html = fetch(COMPANIES_URL)
    except SystemExit:
        return {}
    soup = BeautifulSoup(html, "html.parser")
    by_name = {}
    for card in soup.select(".reach-portfolio-card"):
        title = card.select_one(".reach-portfolio-card__title")
        name = clean(title.get_text()) if title else None
        if not name:
            continue
        desc_el = card.select_one(".reach-portfolio-card__desc, .reach-portfolio-card__info")
        desc = None
        if desc_el:
            # first substantial text
            t = clean(desc_el.get_text(" ", strip=True))
            if t:
                # strip leading tag words like Learning Exit
                desc = t
        tags = [clean(x.get_text()) for x in card.select(".reach-portfolio-card__tag")]
        tags = [t for t in tags if t]
        status = "Exited" if any(t.lower() in ("exit", "exited", "partial exit") for t in tags) else "Active"
        sectors = [t for t in tags if t.lower() not in ("exit", "exited", "partial exit", "active", "pre-seed")]
        founded = None
        hq = None
        text = card.get_text("\n", strip=True)
        for line in text.split("\n"):
            line = clean(line)
            if line and line.lower().startswith("founded"):
                founded = line.split(" ", 1)[-1] if " " in line else None
            if line and line.lower().startswith("headquarters"):
                hq = line.split(" ", 1)[-1] if " " in line else None
        by_name[name.lower()] = {
            "description": desc if desc and len(desc) >= 20 else None,
            "status": status,
            "sectors": sectors,
            "location": hq,
            "founded": founded,
        }
    return by_name


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    cards = load_html_cards()
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    page = 1
    while True:
        r = fetch_response(f"{API}?per_page=100&page={page}")
        items = r.json()
        if not items:
            break
        for it in items:
            name = clean(unescape((it.get("title") or {}).get("rendered") or ""))
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            sectors = [SECTOR_MAP[i] for i in (it.get("sector") or []) if i in SECTOR_MAP]
            status_ids = it.get("portfolio-status") or []
            status = "Active"
            stage = None
            for sid in status_ids:
                lab = STATUS_MAP.get(sid)
                if lab in ("Exit", "Partial Exit"):
                    status = "Exited"
                elif lab == "Pre-Seed":
                    stage = "Pre-Seed"  # funding-round-like label present on firm taxonomy
                elif lab == "Active":
                    status = "Active"
            card = cards.get(key) or {}
            if card.get("status") == "Exited":
                status = "Exited"
            for s in card.get("sectors") or []:
                if s not in sectors:
                    sectors.append(s)
            desc = card.get("description")
            tag_seed = list(sectors)
            tags = []
            for s in sectors:
                for t in SECTOR_TAGS.get(s, []):
                    if t not in tags:
                        tags.append(t)
            for t in classify(name, desc, tag_seed):
                if t not in tags:
                    tags.append(t)
            rec = {
                "company_name": name,
                "description": desc,
                "company_url": None,
                "location": card.get("location"),
                "status": status,
                "stage": stage,
                "sectors": sectors,
                "everywhere_tags": tags[:4],
                "primary_investor": PRIMARY,
                "source_url": it.get("link") or COMPANIES_URL,
                "scraped_at": scraped_at,
            }
            out.append(rec)
            if limit and len(out) >= limit:
                break
        if limit and len(out) >= limit:
            break
        total_pages = int(r.headers.get("X-WP-TotalPages") or "1")
        if page >= total_pages:
            break
        page += 1

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged")


if __name__ == "__main__":
    main()
