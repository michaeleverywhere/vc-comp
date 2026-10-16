#!/usr/bin/env python3
"""IQ Capital portfolio scraper -> iqcapital_companies.json
Source: https://www.iqcapital.vc/companies — Webflow companies-feed_card
(name, one-liner, optional /company/slug detail, data-feed-exit stage/status).
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, stage_label, fetch_many
from _d20_common import write_out

SOURCE_URL = "https://www.iqcapital.vc/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "iqcapital_companies.json")
PRIMARY = "IQ Capital"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = []
    for c in soup.select(".companies-feed_card"):
        name = None
        for el in c.select("[fs-cmssort-field='name']"):
            t = clean(el.get_text(" "))
            if t:
                name = t
                break
        if not name or name.lower() == "stealth":
            # keep stealth only if unique? skip unnamed stealth placeholders
            if not name or name.lower() == "stealth":
                continue
        a = c.select_one("a.companies-feed_card-link[href]")
        detail = urljoin(SOURCE_URL, a["href"]) if a and a.get("href") else None
        desc_el = c.select_one(".companies-feed_card-description")
        desc = clean(desc_el.get_text(" ")) if desc_el else None
        exit_raw = clean(c.get("data-feed-exit"))
        stage = status = None
        if exit_raw:
            el = exit_raw.lower()
            if el in ("exited", "acquired"):
                status = "acquired"
            elif el in ("active", "live"):
                status = "active"
            else:
                stage = stage_label(exit_raw)
        cards.append((name, desc, detail, stage, status))

    # enrich website from detail pages when published
    details = [d for _, _, d, _, _ in cards if d]
    pages = fetch_many(details, workers=6, pause=0.12)
    out, seen = [], set()
    for name, desc, detail, stage, status in cards:
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        website = None
        if detail and pages.get(detail):
            ds = BeautifulSoup(pages[detail], "html.parser")
            for a in ds.select("a[href^=http]"):
                href = a["href"]
                label = (clean(a.get_text(" ")) or "").lower()
                if "iqcapital" in href:
                    continue
                if label in ("website", "visit website", "company website") or (
                    label and "website" in label and len(label) < 30
                ):
                    website = clean_url(href)
                    break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "stage": stage,
            "status": status,
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "stage", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
