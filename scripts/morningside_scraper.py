#!/usr/bin/env python3
"""Morningside Ventures portfolio scraper -> morningside_companies.json
Source: https://morningside.com/today/portfolio/venture/ — venture portfolio tree
(sector -> sub-sector pages): company name, tagline, description, website and the
site's sector path."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://morningside.com/today/portfolio/venture/"
PRIMARY = "Morningside Ventures"


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
    seen, todo, rows = set(), [SOURCE_URL], {}
    while todo:
        u = todo.pop(0)
        if u in seen:
            continue
        seen.add(u)
        s = soup_of(u)
        for a in s.select("a.section-content__link[href]"):
            v = urljoin(u, a["href"])
            if v.startswith(SOURCE_URL) and v not in seen:
                todo.append(v)
        path = [txt(x).rstrip(" ›").strip() for x in s.select(".section-header__breadcrumbs-link a")]
        path = [p for p in path if p and p not in ("Portfolio", "Venture")]
        for sl in s.select(".swiper-slide"):
            nm = txt(sl.select_one(".swiper-slide__company"))
            if not nm:
                continue
            ps = [p for p in sl.select("p") if txt(p)]
            tag = txt(ps[0].find("strong")) if ps and ps[0].find("strong") else None
            desc = " ".join(txt(p) for p in ps if not (p.find("strong") and txt(p) == txt(p.find("strong"))) and not
                            (p.find("a") and txt(p) == txt(p.find("a")))) or None
            web = next((site(x) for x in sl.select("a[href^=http]") if site(x) and "morningside.com" not in x["href"]), None)
            r = rows.get(nm.lower())
            if r:
                r["sectors"] += [p for p in path if p not in r["sectors"]]
                continue
            rows[nm.lower()] = {"name": nm, "desc": clean(desc), "web": web, "tag": tag, "sectors": list(path)}
    for r in rows.values():
        out.append(rec(r["name"], r["desc"] or r["tag"], r["web"], PRIMARY, SOURCE_URL, scraped_at, sectors=r["sectors"], tagline=r["tag"]))
    finish(out, "morningside", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
