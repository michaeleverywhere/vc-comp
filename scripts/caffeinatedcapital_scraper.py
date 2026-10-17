#!/usr/bin/env python3
"""Caffeinated Capital portfolio scraper -> caffeinatedcapital_companies.json
Source: https://www.caffeinated.com/ — homepage cards: company cards (name and one-line
mission) plus founder cards (company from the card's role line, e.g. 'CEO & Co-Founder / Airtable')."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.caffeinated.com/"
PRIMARY = "Caffeinated Capital"


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
    seen = []
    comp, fnd = [], []
    for n in s.select("div.grid-card-list-item.is-name"):
        h = n.find_next_sibling(class_="is-history")
        if not h:
            continue
        nm = txt(n)
        parts = [clean(x) for x in h.stripped_strings]
        if not nm or not parts:
            continue
        if len(parts) == 1:
            comp.append((nm, parts[0]))
        elif len(parts) <= 3 and re.search(r"(?i)founder", parts[0]) and len(parts[-1].split()) <= 6:
            fnd.append(parts[-1])
    for nm, d in comp:
        if nm.lower() not in seen and len(nm.split()) <= 5:
            seen.append(nm.lower())
            out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at))
    for nm in fnd:
        k = nm.lower()
        if re.search(r"(?i)caffeinated|stealth", nm) or any(k.startswith(x) or x.startswith(k) for x in seen):
            continue
        seen.append(k)
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "caffeinatedcapital", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
