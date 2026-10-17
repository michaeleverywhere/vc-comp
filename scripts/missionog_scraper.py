#!/usr/bin/env python3
"""MissionOG portfolio scraper -> missionog_companies.json
Source: https://missionog.com/partner-companies/ — partner companies page: company name
(h2), description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://missionog.com/partner-companies/"
PRIMARY = "MissionOG"


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
    for h in s.select("h2.headingTitleCaps"):
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        box = h.find_parent("div", class_="p_body") or h.find_parent("div")
        p = next((x for x in box.find_all(["p", "div"]) if not x.find(["h2", "a", "div"]) and len(x.get_text(strip=True)) > 40), None) if box else None
        a = box.find("a", href=True) if box else None
        out.append(rec(nm, txt(p), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "missionog", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
