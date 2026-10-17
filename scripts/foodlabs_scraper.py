#!/usr/bin/env python3
"""FoodLabs portfolio scraper -> foodlabs_companies.json
Source: https://www.foodlabs.com/portfolio — Webflow portfolio cards: company name (logo alt),
categories, stage, tagline and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.foodlabs.com/portfolio"
PRIMARY = "FoodLabs"


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
    seen = set()
    for it in s.select("div.portfolio-item.w-dyn-item"):
        img = it.select_one("img[alt]")
        nm = clean(img.get("alt")) if img else None
        p = [clean(x) for x in it.stripped_strings if clean(x)]
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        i = p.index(nm) if nm in p else None
        tags = p[:i] if i is not None else []
        stage = it.get("data-stage")
        a = it.select_one("a[href^=http]")
        out.append(rec(nm, p[i + 1] if i is not None and len(p) > i + 1 else None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[t for t in tags if t.lower().replace(" ", "-") != (stage or "")], stage=stage.replace("-", " ").title() if stage else None))
    finish(out, "foodlabs", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
