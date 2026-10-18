#!/usr/bin/env python3
"""AfterWork Ventures portfolio scraper -> afterwork_companies.json
Source: https://www.afterwork.vc/portfolio — Webflow CMS: the full company grid
(name, website, AfterWork sector label, "invested in YYYY" = first invested, and the
"Acquired" badge when it is not hidden) plus the current-portfolio modals (website,
investment-memo link, description when filled)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.afterwork.vc/portfolio"
PRIMARY = "AfterWork Ventures"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "healthtech": ["Health"], "proptech": ["PropTech"],
              "climate": ["Climate / Sustainability"], "climatetech": ["Climate / Sustainability"],
              "dev tools": ["Dev Tools / Cloud"], "devtools": ["Dev Tools / Cloud"], "web3": ["Web3 / Crypto"],
              "logistics": ["Logistics / Supply Chain"], "consumer": ["Consumer"], "hr tech": ["Future of Work"],
              "edtech": ["Future of Work"], "cybersecurity": ["Cybersecurity"], "insurtech": ["FinTech / Insurance"]}


def visible(el):
    return el is not None and "w-condition-invisible" not in (el.get("class") or []) and \
        "w-dyn-bind-empty" not in (el.get("class") or [])


def info(card):
    bits = [clean(h.get_text(" ", strip=True)) for h in card.select(".company-information") if visible(h)]
    sector = bits[0] if bits else None
    yr = next((int(b) for b in bits if b and re.fullmatch(r"\d{4}", b)), None)
    return sector if sector and not sector.startswith(",") else None, yr


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows = {}
    for it in s.select(".portfolio_item.w-dyn-item"):
        n = it.select_one(".company-name")
        name = clean(n.get_text(" ", strip=True)) if n else None
        if not name:
            continue
        sector, yr = info(it)
        web = next((a["href"] for a in it.select(".socials-wrapper a[href^=http]") if not is_social(a["href"])), None)
        memo = next((a["href"] for a in it.select("a[href]") if "investment-notes" in a["href"]), None)
        d = it.select_one(".modal-portfolio-content .w-richtext")
        rows[name.lower()] = dict(name=name, sector=sector, yr=yr, web=web, memo=memo, acquired=False,
                                  desc=clean(d.get_text(" ", strip=True)) if visible(d) else None)
    for it in s.select(".collection-item-4.w-dyn-item"):
        n = it.select_one(".company-name")
        name = clean(n.get_text(" ", strip=True)) if n else None
        if not name:
            continue
        a = it.select_one("a[href^=http]")
        sector, yr = info(it)
        badge = it.select_one(".div-block-47")
        acq = visible(badge) and "acquired" in (badge.get_text(" ", strip=True) or "").lower()
        r = rows.setdefault(name.lower(), dict(name=name, sector=sector, yr=yr, web=None, memo=None, desc=None, acquired=False))
        r["web"] = r["web"] or (a["href"] if a and not is_social(a["href"]) else None)
        r["sector"], r["yr"] = r["sector"] or sector, r["yr"] or yr
        r["acquired"] = r["acquired"] or acq
    out = [rec(r["name"], r["desc"], r["web"], PRIMARY, SOURCE_URL, scraped_at,
               sectors=[r["sector"]] if r["sector"] else [], sector_map=SECTOR_MAP, sector_label=r["sector"],
               first_invested=r["yr"], investment_memo=r["memo"], status="acquired" if r["acquired"] else "active")
           for r in rows.values()]
    finish(out, "afterwork", ("company_url", "sector_label", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
