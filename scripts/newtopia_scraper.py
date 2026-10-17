#!/usr/bin/env python3
"""Newtopia VC portfolio scraper -> newtopia_companies.json
Source: https://newtopia.vc/portfolio/ — Elementor portfolio grid: company name,
one-line description (image caption), sector filter and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://newtopia.vc/portfolio/"
PRIMARY = "Newtopia VC"


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
    flt = {li.get("data-filter"): txt(li) for li in s.select("li.elementor-portfolio__filter") if li.get("data-filter") not in (None, "__all")}
    for it in s.select("article.elementor-portfolio-item"):
        nm = txt(it.select_one(".elementor-portfolio-item__title"))
        if not nm:
            continue
        alt = clean((it.find("img") or {}).get("alt") if it.find("img") else None) or ""
        alt = re.sub(r"\s*\|\s*Newtopia VC portfolio\s*$", "", alt)
        d = clean(alt.split(" – ", 1)[1]) if " – " in alt else None
        cats = [flt[c[len("elementor-filter-"):]] for c in (it.get("class") or []) if c.startswith("elementor-filter-") and c[len("elementor-filter-"):] in flt]
        a = it.select_one("a[href]")
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at, sectors=cats, detail_url=a["href"] if a else None))
    finish(out, "newtopia", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
