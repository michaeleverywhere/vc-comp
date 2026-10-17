#!/usr/bin/env python3
"""Wavemaker 360 portfolio scraper -> wavemaker360_companies.json
Source: https://www.wavemaker360.com/portfolio — Wix portfolio repeater: tagline and LEARN MORE
link; company name from each company page title."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.wavemaker360.com/portfolio"
PRIMARY = "Wavemaker 360"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    items = []
    for it in s.select(".wixui-repeater__item"):
        a = next((x for x in it.select("a[href*='/portfolio/']")), None)
        if not a:
            continue
        ts = [txt(x) for x in it.select(".wixui-rich-text") if txt(x)]
        items.append((a["href"], ts[0] if ts else None))
    pages = fetch_many(list(dict.fromkeys(u for u, _ in items)))
    soups = {u: BeautifulSoup(h, "html.parser") for u, h in pages.items() if h}
    common = {}
    for d in soups.values():
        for h in {x["href"] for x in d.select("a[href^='http']")}:
            common[h] = common.get(h, 0) + 1
    for u, tag in items:
        d = soups.get(u)
        if not d:
            continue
        t = txt(d.title) or ""
        nm = clean(t.split(" | ")[0])
        if not nm or nm.lower().startswith("portfolio"):
            continue
        web = next((x for x in d.select("a[href^='http']") if site(x) and common.get(x["href"], 0) <= 2
                    and not any(w in x["href"] for w in ("wavemaker", "wix", "google.com"))), None)
        out.append(rec(nm, tag, site(web), PRIMARY, SOURCE_URL, scraped_at, detail_url=u))
    finish(out, "wavemaker360", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
