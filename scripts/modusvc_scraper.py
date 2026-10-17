#!/usr/bin/env python3
"""Modus Capital portfolio scraper -> modusvc_companies.json
Source: https://modus.vc/portfolio/ — portfolio cards: company name, sector, fund,
country, description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://modus.vc/portfolio/"
PRIMARY = "Modus Capital"


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
    for h in s.select("h3"):
        nm = txt(h)
        par = h.parent
        ss = [clean(x) for x in par.stripped_strings if clean(x)]
        if not nm or nm.lower() in seen or len(ss) < 4 or ss[0] != nm:
            continue
        seen.add(nm.lower())
        a = h.find_parent("a", href=re.compile(r"^https?://")) or par.find("a", href=re.compile(r"^https?://"))
        d = next((x for x in ss[1:] if len(x) > 40), None)
        out.append(rec(nm, d, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, sector=ss[1], fund=ss[2], country=ss[3] if len(ss) > 4 else None))
    finish(out, "modusvc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
