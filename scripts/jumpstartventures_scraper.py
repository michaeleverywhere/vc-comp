#!/usr/bin/env python3
"""JumpStart Ventures portfolio scraper -> jumpstartventures_companies.json
Source: https://jumpstart.vc/portfolio/ — Avada portfolio grid: company name, category
and detail page; description and website from each company page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://jumpstart.vc/portfolio/"
PRIMARY = "JumpStart Ventures"


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
    for it in s.select(".fusion-portfolio-content-wrapper"):
        nm = txt(it.select_one(".entry-title"))
        a = it.select_one("a[href*='/portfolio-company/']") or it.select_one(".entry-title a")
        if nm:
            cats = [txt(x) for x in it.select(".fusion-portfolio-meta a, .fusion-portfolio-categories a") if txt(x)]
            items.append((nm, a["href"] if a else None, cats))
    pages = fetch_many([u for _, u, _ in items if u])
    for nm, u, cats in items:
        desc = web = None
        h = pages.get(u) if u else None
        if h:
            d = BeautifulSoup(h, "html.parser")
            body = d.select_one(".post-content") or d.select_one(".fusion-content-tb") or d
            desc = next((txt(p) for p in body.select("p") if txt(p) and len(txt(p)) > 40), None)
            web = next((x for x in body.select("a[href^='http']") if site(x) and "jumpstart" not in x["href"]), None)
        out.append(rec(nm, desc, site(web), PRIMARY, SOURCE_URL, scraped_at, sectors=cats, detail_url=u))
    finish(out, "jumpstartventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
