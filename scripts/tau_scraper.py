#!/usr/bin/env python3
"""Tau Ventures portfolio scraper -> tau_companies.json
Source: https://www.tauventures.com/portfolio — company cards: name, category (data-category), exited
flag (data-exited), investment-stage note and website (ref param stripped)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.tauventures.com/portfolio"
PRIMARY = "Tau Ventures"


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
    for a in s.select("a.company-card-desktop"):
        nm = txt(a.find("h3"))
        if not nm:
            continue
        stage = None
        lab = next((p for p in a.find_all("p") if txt(p) == "Inv. Stage"), None)
        if lab:
            stage = txt(lab.find_next_sibling("p"))
        web = site(a)
        web = re.sub(r"[?&]ref=tauventures\.com$", "", web) if web else None
        cat = clean(a.get("data-category"))
        out.append(rec(nm, None, web, PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [], stage=stage,
                       status="exited" if a.get("data-exited") == "true" else None))
    finish(out, "tau", ("company_url", "stage", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
