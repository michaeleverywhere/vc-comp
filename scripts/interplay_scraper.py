#!/usr/bin/env python3
"""Interplay portfolio scraper -> interplay_companies.json
Source: https://www.interplay.vc/portfolio — Webflow CMS portfolio cards: company name (detail link
/portfolio/<slug>), description, website, status and Interplay relationship
tags (Ventures / Studio / Accelerator / Secondary / Ascend)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.interplay.vc/portfolio"
PRIMARY = "Interplay"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    s = BeautifulSoup(fetch(url), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for it in s.select(".w-dyn-item"):
        card = it.find(class_="portfolio-logo-card_component", recursive=False)
        nm = it.find("a", class_="hide", recursive=False)
        if not card or not nm or not txt(nm):
            continue
        rel = sorted({txt(x) for x in card.select("[fs-cmsfilter-field='relationships']") if txt(x)})
        st = card.select_one("[fs-cmsfilter-field='status']")
        st = txt(st) if st and "w-dyn-bind-empty" not in (st.get("class") or []) else None
        out.append(rec(txt(nm), txt(card.select_one(".portfolio-logo-card_text")), site(card.select_one("a.portfolio-card_link")),
                       PRIMARY, SOURCE_URL, scraped_at, relationship=", ".join(rel) or None, portfolio_status=st,
                       status="acquired" if st and "acqui" in st.lower() else None,
                       detail_url=urljoin(SOURCE_URL, nm["href"]) if nm.get("href") else None))
    finish(out, "interplay", ("description", "company_url", "relationship", "everywhere_tags"))


if __name__ == "__main__":
    main()
