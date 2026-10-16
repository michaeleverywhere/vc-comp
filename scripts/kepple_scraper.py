#!/usr/bin/env python3
"""Kepple Africa Ventures portfolio scraper -> kepple_companies.json
Source: https://vkav.vc/portfolio/ — Bricks-built portfolio (Verod-Kepple Africa Ventures);
each company popup gives name, website, investment stage and description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://vkav.vc/portfolio/"
PRIMARY = "Kepple Africa Ventures"


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
    for p in s.select("div.brx-popup[data-popup-loop-id]"):
        nm = txt(p.find("h3"))
        if not nm:
            continue
        a = next((x for x in p.find_all("a", href=True) if "View Website" in x.get_text()), None)
        stage = None
        lab = next((x for x in p.find_all("p") if txt(x) == "Investment Stage"), None)
        if lab:
            stage = txt(lab.find_next(["h5", "h4", "p"]))
        paras = [txt(x) for x in p.find_all("p") if txt(x) and txt(x) != "Investment Stage" and "label" not in (x.get("class") or [])]
        desc = max(paras, key=len) if paras else None
        out.append(rec(nm, desc, site(a), PRIMARY, SOURCE_URL, scraped_at, stage=stage))
    finish(out, "kepple", ("description", "company_url", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
