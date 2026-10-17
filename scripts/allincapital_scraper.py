#!/usr/bin/env python3
"""All In Capital portfolio scraper -> allincapital_companies.json
Source: https://www.allincapital.vc/portfolio — portfolio cards with popups: company
name, sectors, notes and website; plus the 'Past Portfolio Companies' names."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.allincapital.vc/portfolio"
PRIMARY = "All In Capital"


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
    for p in s.select("div.portfolio-popup"):
        sp = [txt(x) for x in p.select("span")]
        nm = sp[0] if sp else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        sec = sp[1] if len(sp) > 1 else None
        w = next((site(a) for a in p.select("a[href^=http]") if site(a)), None)
        out.append(rec(nm, txt(p.select_one("p")), w, PRIMARY, SOURCE_URL, scraped_at, sectors=[x.strip() for x in sec.split(",")] if sec else []))
    h = next((h for h in s.select("h3") if "Past Portfolio" in h.get_text()), None)
    if h:
        for e in h.find_all_next("h3"):
            nm = txt(e)
            if nm and nm.lower() not in seen:
                seen.add(nm.lower())
                out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, holding="past"))
    finish(out, "allincapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
