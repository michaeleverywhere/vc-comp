#!/usr/bin/env python3
"""Five Four Ventures portfolio scraper -> fivefour_companies.json
Source: https://www.fivefourventures.com/ — homepage company rows: company name, category
(with acquisition note) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.fivefourventures.com/"
PRIMARY = "Five Four Ventures"


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
    for a in s.select("a.company-row"):
        nm = txt(a.select_one(".company-row__name"))
        if not nm:
            continue
        cat = txt(a.select_one(".company-row__cat")) or ""
        parts = [clean(x) for x in cat.split("·")]
        acq = next((x for x in parts if x and re.match(r"(?i)acq", x)), None)
        sec = next((x for x in parts if x and not re.match(r"(?i)acq", x)), None)
        acq_note = clean(re.sub(r"(?i)^acq\.?(uired)?\s*by", "Acquired by", acq)) if acq else None
        out.append(rec(nm, sec, None if acq else site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [],
                       exit_note=acq_note, status="acquired" if acq else None))
    finish(out, "fivefour", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
