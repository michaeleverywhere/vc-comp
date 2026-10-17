#!/usr/bin/env python3
"""Lakehouse Ventures portfolio scraper -> lakehouse_companies.json
Source: https://lakehouse.vc/portfolio/ — Astro portfolio list (name, tagline, stage,
investment date, location) plus each /portfolio/<slug> page: description, founders and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://lakehouse.vc/portfolio/"
PRIMARY = "Lakehouse Ventures"


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
    for a in s.select("a.company-list-item"):
        nm = txt(a.select_one(".company-name"))
        if nm:
            items.append((nm, a, urljoin(SOURCE_URL, a["href"])))
    pages = fetch_many([u for _, _, u in items])
    for nm, a, u in items:
        d = BeautifulSoup(pages.get(u) or "", "html.parser")
        web = next((x for x in d.select("a[href^='http']") if txt(x) == "Website"), None)
        body = d.find("main") or d
        lab = {}
        for e in body.find_all(string=re.compile(r"^\s*(Founders?|Invested|Location)\s*$")):
            nxt = e.parent.find_next_sibling()
            if nxt:
                lab[clean(e)] = txt(nxt)
        desc = None
        h = body.find(["h1", "h2"], string=re.compile(r"^\s*" + re.escape(nm) + r"\s*$"))
        if h:
            p = h.find_next("p")
            desc = txt(p)
        stage = txt(a.select_one("span.sans"))
        stage = clean(re.sub(r",.*$", "", stage or "")) or None
        date = a.get("data-date")
        out.append(rec(nm, desc or txt(a.select_one(".company-description")), site(web), PRIMARY, SOURCE_URL, scraped_at,
                       tagline=txt(a.select_one(".company-description")), stage=stage, invested_date=date, year=year_of(date),
                       location=txt(a.select_one(".company-location")),
                       founders=[clean(x) for x in re.split(r",| and ", lab.get("Founders") or lab.get("Founder") or "") if clean(x)],
                       detail_url=u))
    finish(out, "lakehouse", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
