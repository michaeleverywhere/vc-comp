#!/usr/bin/env python3
"""Emerging Ventures portfolio scraper -> emergingventures_companies.json
Source: https://emerging.vc/portfolio — portfolio cards: description, tags, status and
location; company name from each company page heading."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://emerging.vc/portfolio"
PRIMARY = "Emerging Ventures"


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
    cards = []
    for c in s.select("[class*='CompanyCard_root']"):
        a = c.select_one("a[href*='/portfolio/']")
        if not a:
            continue
        u = urljoin(SOURCE_URL, a["href"])
        tags = [txt(x) for x in c.select("[class*='Tag_root'] p") if txt(x)]
        st = txt(c.select_one("[class*='CompanyCard_status'] span")) or ""
        loc = txt(c.select_one("[class*='CompanyCard_locationContainer'] p"))
        web = next((x for x in c.select("a[href^='http']") if site(x) and "emerging.vc" not in x["href"]), None)
        cards.append((u, txt(c.select_one("[class*='CompanyCard_descriptionContainer']")), tags, st, loc, site(web)))
    pages = fetch_many([x[0] for x in cards])
    for u, desc, tags, st, loc, web in cards:
        h = pages.get(u)
        nm = txt(BeautifulSoup(h, "html.parser").select_one("h1")) if h else None
        if not nm:
            continue
        out.append(rec(nm, desc, web, PRIMARY, SOURCE_URL, scraped_at, sectors=tags, location=loc, portfolio_status=st or None,
                       status="exited" if "exit" in st.lower() else ("active" if "active" in st.lower() else None), detail_url=u))
    finish(out, "emergingventures", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
