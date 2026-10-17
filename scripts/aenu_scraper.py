#!/usr/bin/env python3
"""AENU portfolio scraper -> aenu_companies.json
Source: https://www.aenu.com/portfolio/ — portfolio gallery: company name and profile slug
from the page's own company list (also shown as image alts)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.aenu.com/portfolio/"
PRIMARY = "AENU"


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
    import json, html as _h
    s = soup_of(SOURCE_URL)
    seen = set()
    for el in s.find_all(attrs={"x-data": True}):
        m = re.search(r"companies:\s*(\[.*?\])\s*,\s*\w+\s*:", el["x-data"], re.S)
        if not m:
            continue
        try:
            arr = json.loads(_h.unescape(m.group(1)))
        except Exception:
            continue
        for c in arr:
            nm = clean(c.get("name") or "")
            if not nm or nm.lower() in seen:
                continue
            seen.add(nm.lower())
            u = c.get("website") or c.get("url")
            out.append(rec(nm, clean(c.get("description") or c.get("tagline") or "") or None, u if isinstance(u, str) and u.startswith("http") else None,
                           PRIMARY, SOURCE_URL, scraped_at, profile_url=urljoin(SOURCE_URL, c["slug"] + "/") if c.get("slug") else None))
    if not out:
        for img in s.find_all("img", alt=True):
            nm = clean(img["alt"])
            if nm and "hero image" not in nm and "portfolio companies" not in nm.lower() and nm.lower() not in seen:
                seen.add(nm.lower())
                out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "aenu", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
