#!/usr/bin/env python3
"""Script Capital portfolio scraper -> script_companies.json
Source: https://script.capital/ — homepage company grid: company name, one-line
description, site tags, acquisition note and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://script.capital/"
PRIMARY = "Script Capital"


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
    for a in s.select("a[href^='/companies/']"):
        nm = txt(a.select_one("h3"))
        if not nm:
            continue
        nm = clean(re.split(r"\s+·\s+", nm, maxsplit=1)[0])  # drop the " · acq. by X" suffix
        try:
            tags = [t for t in json.loads(a.get("data-tags") or "[]") if t and t.lower() != "featured"]
        except ValueError:
            tags = []
        note = next((txt(x) for x in a.select("span.text-xs") if txt(x) and "acq" in txt(x).lower()), None)
        note = clean(note.lstrip("·").strip()) if note else None
        out.append(rec(nm, txt(a.select_one("p")), None, PRIMARY, SOURCE_URL, scraped_at, sectors=tags, exit_note=note,
                       status="acquired" if note else None, detail_url=urljoin(SOURCE_URL, a["href"])))
    finish(out, "script", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
