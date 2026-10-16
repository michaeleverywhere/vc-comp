#!/usr/bin/env python3
"""JLL Spark portfolio scraper -> jllspark_companies.json
Source: https://spark.jllt.com/portfolio/ — WordPress portfolio boxes (JLL's proptech venture arm):
company name (logo link title / alt), one-line description, website and exit tag."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://spark.jllt.com/portfolio/"
PRIMARY = "JLL Spark"


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
    for it in s.select(".team-template-box"):
        a = it.select_one(".team-template-box-img a")
        img = it.select_one(".team-template-box-img img")
        nm = clean(a.get("title")) if a and a.get("title") else (clean(img.get("alt")) if img else None)
        if not nm:
            continue
        tag = txt(it.select_one(".portfolio-tag"))
        desc = next((txt(p) for p in it.select(".team-template-box-data p") if "portfolio-tag" not in (p.get("class") or [])), None)
        web = site(a).split("#")[0] if site(a) else None
        out.append(rec(nm, desc, web, PRIMARY, SOURCE_URL, scraped_at, exit_note=tag,
                       status="exited" if tag and tag.lower().startswith("exited") else None))
    finish(out, "jllspark", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
