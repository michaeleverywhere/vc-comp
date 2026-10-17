#!/usr/bin/env python3
"""Waarde Capital portfolio scraper -> waardecapital_companies.json
Source: https://waardecapital.com/ — homepage holdings: company name with website,
country label, tagline, description and exit note."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://waardecapital.com/"
PRIMARY = "Waarde Capital"


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
    for col in s.select(".col"):
        a = col.select_one(".hold-title h3 a") or col.select_one(".hold-title a")
        nm = txt(a)
        if not nm:
            continue
        tags = [x for x in col.select("strong.name-description") if "blue" not in (x.get("class") or [])]
        note = txt(col.select_one("strong.name-description.blue"))
        desc = clean(" ".join(txt(p) or "" for p in col.select("p"))) or (txt(tags[0]) if tags else None)
        out.append(rec(nm, desc, site(a), PRIMARY, SOURCE_URL, scraped_at, tagline=txt(tags[0]) if tags else None,
                       country=txt(col.select_one(".label")), exit_note=note,
                       status="exited" if note and any(w in note.lower() for w in ("acquir", "exit", "ipo")) else None))
    finish(out, "waardecapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
