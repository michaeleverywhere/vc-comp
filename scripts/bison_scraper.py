#!/usr/bin/env python3
"""Bison Ventures portfolio scraper -> bison_companies.json
Source: https://www.bison.vc/ — Portfolio list: company name, description,
leadership, focus area and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.bison.vc/"
PRIMARY = "Bison Ventures"


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
    for li in s.select("li.portfolio-company-item"):
        b = li.select_one("button.portfolio-company-trigger")
        nm = clean(b.get_text(" ", strip=True)) if b else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ex = li.select_one(".portfolio-company-expanded-content")
        p = [clean(x) for x in ex.stripped_strings] if ex else []
        def lab(l):
            return p[p.index(l) + 1] if l in p and p.index(l) + 1 < len(p) else None
        fa = lab("FOCUS AREA")
        web = next((site(a) for a in li.select("a[href^=http]") if site(a)), None)
        out.append(rec(nm, txt(li.select_one(".portfolio-company-description")), web, PRIMARY, SOURCE_URL, scraped_at,
                       leadership=lab("LEADERSHIP"), sectors=[fa] if fa else []))
    finish(out, "bison", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
