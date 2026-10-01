#!/usr/bin/env python3
"""Greycroft portfolio scraper -> greycroft_companies.json
Source: https://www.greycroft.com/wp-json/wp/v2/portfolio (paginated).
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone
from html import unescape

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, html_text

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

API = "https://www.greycroft.com/wp-json/wp/v2/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "greycroft_companies.json")
PRIMARY = "Greycroft"
SOURCE_URL = "https://www.greycroft.com/portfolio"

STATUS_MAP = {9: "Acquired", 10: "Active", 11: "IPO", 27: "Acquired"}
STAGE_MAP = {12: "Early", 13: "Growth"}
# Early/Growth are stage labels on firm site — not funding rounds; leave stage blank unless clearly a round.
STRATEGY_MAP = {14: "Consumer Brands", 15: "Technology", 16: "Sustainability"}


def parse_card_html(card_html):
    if not card_html:
        return {}
    soup = BeautifulSoup(card_html, "html.parser")
    status_el = soup.select_one(".portfolio-card__status")
    status = clean(status_el.get_text()) if status_el else None
    year_el = soup.select_one(".portfolio-card__year")
    year = clean(year_el.get_text()) if year_el else None
    stage_el = soup.select_one(".portfolio-card__stage-type")
    stage_label = clean(stage_el.get_text()) if stage_el else None
    desc = None
    for p in soup.select(".portfolio-card__accordion p"):
        t = clean(p.get_text())
        if t and len(t) >= 20 and t.lower() not in ("technology", "early", "growth", "consumer brands", "sustainability"):
            desc = t
            break
    website = None
    for a in soup.select("a[href^='http']"):
        href = a["href"]
        if "greycroft.com" in href:
            continue
        website = clean(href)
        break
    logo = None
    img = soup.select_one("img.portfolio-card__image")
    if img and img.get("src"):
        logo = clean(img["src"])
    return {"status_label": status, "year": year, "stage_label": stage_label, "description": desc, "company_url": website, "logo_url": logo}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    page = 1
    while True:
        r = fetch_response(f"{API}?per_page=100&page={page}")
        items = r.json()
        if not items:
            break
        for it in items:
            title = it.get("title") or {}
            name = clean(unescape(title.get("rendered") or ""))
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            card = parse_card_html(it.get("card") or "")
            excerpt = html_text((it.get("excerpt") or {}).get("rendered") or "")
            content = html_text((it.get("content") or {}).get("rendered") or "")
            desc = card.get("description") or excerpt or content
            status_ids = it.get("portfolio_status") or []
            status = "Active"
            for sid in status_ids:
                lab = STATUS_MAP.get(sid)
                if lab == "Active":
                    status = "Active"
                elif lab in ("Acquired", "IPO"):
                    status = "Exited"
                    break
            if card.get("status_label"):
                sl = card["status_label"].lower()
                if sl == "active":
                    status = "Active"
                elif sl in ("acquired", "ipo") or "acquired" in sl:
                    status = "Exited"
            strategies = [STRATEGY_MAP[i] for i in (it.get("portfolio_strategy") or []) if i in STRATEGY_MAP]
            rec = {
                "company_name": name,
                "description": desc,
                "company_url": card.get("company_url"),
                "logo_url": card.get("logo_url"),
                "status": status,
                "exit_detail": card.get("status_label") if status == "Exited" else None,
                "stage": None,  # Early/Growth are firm labels, not funding rounds
                "investment_year": card.get("year"),
                "strategy": strategies,
                "everywhere_tags": classify(name, desc, strategies)[:4],
                "primary_investor": PRIMARY,
                "source_url": it.get("link") or SOURCE_URL,
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
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged")


if __name__ == "__main__":
    main()
