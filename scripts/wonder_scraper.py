#!/usr/bin/env python3
"""Wonder Ventures portfolio scraper -> wonder_companies.json
Source: https://wondervc.com/portfolio/ — portfolio grid: company name, description,
category classes and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://wondervc.com/portfolio/"
PRIMARY = "Wonder Ventures"


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
    skip = {"col", "elastic-portfolio-item", "element"}
    lab = {a.get("data-filter", "").lstrip("."): txt(a) for a in s.select("[data-filter]") if a.get("data-filter", "").startswith(".")}
    for it in s.select("div.elastic-portfolio-item"):
        nm = txt(it.find("h3"))
        if not nm:
            continue
        cl = [c for c in (it.get("class") or []) if c not in skip]
        cats = [lab.get(c, c.replace("-", " ").title()) for c in cl if c != "exited"]
        out.append(rec(nm, txt(it.select_one(".work-info p")), site(it.select_one(".work-info a")), PRIMARY, SOURCE_URL, scraped_at, sectors=cats,
                       status="exited" if "exited" in cl else None))
    finish(out, "wonder", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
