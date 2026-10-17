#!/usr/bin/env python3
"""Seventure Partners portfolio scraper -> seventure_companies.json
Source: https://www.seventure.fr/expertise/?company=498 — Portfolio list (French): company name, description,
sectors and country."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.seventure.fr/expertise/?company=498"
PRIMARY = "Seventure Partners"


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
    for li in s.select("li.content-partners-expertise"):
        nm = txt(li.select_one("p.title-partners-expertise"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in li.stripped_strings if clean(x) and clean(x) != "Savoir +"]
        ctry = txt(li.select_one(".title-country")) or (p[-1] if len(p) > 3 else None)
        sec = [x for x in p[2:] if x != ctry]
        out.append(rec(nm, p[1] if len(p) > 1 else None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sec, location=ctry))
    finish(out, "seventure", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
