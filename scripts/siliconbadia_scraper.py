#!/usr/bin/env python3
"""Silicon Badia portfolio scraper -> siliconbadia_companies.json
Source: https://www.siliconbadia.com/portfolio/ — portfolio grid (name, location/industry
filter tags, acquired footnote) plus each /portfolio/<slug>/ page: description, industries,
location, fund and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.siliconbadia.com/portfolio/"
PRIMARY = "Silicon Badia"


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
    for li in s.select("li.companies-grid__item"):
        a = li.select_one("a.companies-grid__link")
        img = li.find("img")
        if not a or not img or not clean(img.get("alt")):
            continue
        items.append((clean(img.get("alt")), a["href"], txt(li.select_one(".companies-grid__item__footnote"))))
    pages = fetch_many([u for _, u, _ in items])
    for nm, u, foot in items:
        d = BeautifulSoup(pages.get(u) or "", "html.parser")
        meta = {}
        for sec in d.select(".company__meta__section"):
            h = txt(sec.find("h4"))
            if h:
                meta[h] = sec
        ind = [txt(x) for x in meta["Industries"].select("li")] if "Industries" in meta else []
        loc = [txt(x) for x in meta["Location"].select("li")] if "Location" in meta else []
        fund = [txt(x) for x in meta["Fund"].select("li")] if "Fund" in meta else []
        web = meta["Website"].find("a") if "Website" in meta else None
        st = (foot or "").lower()
        out.append(rec(txt(d.select_one("h1.company__header__title")) or nm, txt(d.select_one(".company__profile")), site(web), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x for x in ind if x], location=", ".join(x for x in loc if x) or None, fund=", ".join(x for x in fund if x) or None,
                       portfolio_status=foot, status="acquired" if "acqui" in st else ("public" if "ipo" in st or "public" in st else None), detail_url=u))
    finish(out, "siliconbadia", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
