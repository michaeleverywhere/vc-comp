#!/usr/bin/env python3
"""M12 portfolio scraper -> m12_companies.json
Source: WP REST /wp-json/wp/v2/portfolio + JetEngine listing pages for websites.
"""
import html as html_lib
import json, os, re, sys, time
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, HEADERS, TIMEOUT

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

API = "https://m12.vc/wp-json/wp/v2/portfolio"
FOCUS_API = "https://m12.vc/wp-json/wp/v2/focus-area"
STAGE_API = "https://m12.vc/wp-json/wp/v2/stage"
LISTING = "https://m12.vc/portfolio/?nocache=1&jsf=jet-engine:portfolio_grid&pagenum={page}"
SOURCE_URL = "https://m12.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "m12_companies.json")
PRIMARY = "M12"


def fetch_json(url, params=None):
    r = requests.get(url, params=params or {}, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json(), r.headers


def fetch_all_portfolio():
    rows, page = [], 1
    while True:
        batch, headers = fetch_json(API, {"per_page": 100, "page": page})
        if not batch:
            break
        rows.extend(batch)
        if page >= int(headers.get("X-WP-TotalPages") or 1):
            break
        page += 1
        time.sleep(0.25)
    return rows


def tax_map(url):
    data, _ = fetch_json(url, {"per_page": 100})
    out = {}
    for t in data:
        name = clean(html_lib.unescape(t.get("name") or ""))
        out[t["id"]] = name
    return out


def norm_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())


def scrape_listing_websites():
    """Return {norm_name: website} from paginated JetEngine listing."""
    mapping = {}
    page = 1
    while page <= 10:
        r = requests.get(LISTING.format(page=page), headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select(".jet-listing-grid__item")
        if not cards:
            break
        for card in cards:
            website = None
            for a in card.select("a[href^='http']"):
                if a.get_text(strip=True).lower() == "visit website":
                    website = clean(a["href"])
                    break
            # name: first text chunk before focus-area labels
            text = clean(card.get_text(" ", strip=True)) or ""
            # strip known suffixes that listing concatenates
            name = re.split(
                r"\b(?:Vertical SaaS|Visit website|Read case study|Deep Tech|Enterprise Applications|"
                r"Cybersecurity|AI Apps|AI Cloud|Security for AI|Developer Tools|Cloud Infrastructure|"
                r"Other)\b",
                text,
                maxsplit=1,
            )[0].strip()
            # Also try heading/title node
            h = card.select_one("h1,h2,h3,h4,.elementor-heading-title")
            if h and clean(h.get_text()):
                name = clean(h.get_text())
            if name and website:
                mapping[norm_key(name)] = website
        if len(cards) < 40 and page > 1:
            # last partial page
            page += 1
            # continue once more then stop if empty next
        page += 1
        time.sleep(0.35)
        if page > 6:
            break
    return mapping


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    focus = tax_map(FOCUS_API)
    stages = tax_map(STAGE_API)
    websites = scrape_listing_websites()
    docs = fetch_all_portfolio()
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for doc in docs:
        name = clean(html_lib.unescape((doc.get("title") or {}).get("rendered") or ""))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        sectors = [focus[i] for i in (doc.get("focus-area") or []) if i in focus]
        stage_labels = [stages[i] for i in (doc.get("stage") or []) if i in stages]
        status = "Active"
        stage = None
        for s in stage_labels:
            sl = s.lower()
            if "exit" in sl:
                status = "Exited"
            elif sl in ("early", "growth", "other", "active"):
                if sl != "active":
                    stage = s
        website = websites.get(norm_key(name))
        # fuzzy: try startswith match
        if not website:
            nk = norm_key(name)
            for k, v in websites.items():
                if k.startswith(nk) or nk.startswith(k):
                    website = v
                    break
        rec = {
            "company_name": name,
            "description": None,
            "company_url": website,
            "status": status,
            "stage": stage,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, None, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": doc.get("link") or SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")
    print(f"  listing website map size: {len(websites)}")


if __name__ == "__main__":
    main()
