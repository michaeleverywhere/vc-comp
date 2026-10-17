#!/usr/bin/env python3
"""Dundee Venture Capital portfolio scraper -> dundeevc_companies.json
Source: https://www.dundeeventurecapital.com/portfolio — Squarespace accordion
(`li.accordion-item`): company name, acquisition note, one-line description,
website, founder and location."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.dundeeventurecapital.com/portfolio"
PRIMARY = "Dundee Venture Capital"


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
    for li in s.select("li.accordion-item"):
        t = txt(li.select_one(".accordion-item__title"))
        if not t:
            continue
        nm, _, d = t.partition("|")
        nm = clean(nm)
        m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", nm or "")
        note = None
        if m:
            nm, note = clean(m.group(1)), clean(m.group(2))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ps = [txt(p) for p in li.select(".accordion-item__description p") if txt(p)]
        loc = next((p.replace("📍", "").strip() for p in ps if p.startswith("📍")), None)
        fd = next((p.replace("💼", "").strip() for p in ps if p.startswith("💼")), None)
        web = next((site(a) for a in li.select(".accordion-item__description a[href^=http]") if site(a)), None)
        acq = note and re.search(r"acq|ipo|merged", note, re.I)
        out.append(rec(nm, clean(d), None if acq else web, PRIMARY, SOURCE_URL, scraped_at, exit_note=note, founders=fd, location=loc,
                       status="acquired" if note and "acq" in note.lower() else None))
    finish(out, "dundeevc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
