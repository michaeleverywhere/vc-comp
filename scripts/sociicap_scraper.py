#!/usr/bin/env python3
"""Socii Capital portfolio scraper -> sociicap_companies.json
Source: https://sociicapital.com/ — homepage portfolio grid: company name (h3),
status label (e.g. IPO / Acquired)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://sociicapital.com/"
PRIMARY = "Socii Capital"


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
        if not nm or nm.lower() in seen or len(nm) > 40:
            continue
        card = h.parent.parent
        img = card.find("img", alt=re.compile(r"(?i)logo"))
        if not img:
            continue
        seen.add(nm.lower())
        ss = [clean(x) for x in card.stripped_strings if clean(x) and clean(x) != nm]
        st = next((x for x in ss if re.match(r"(?i)^(ipo|acquired|exited|spac)$", x)), None)
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, status="exited" if st else None, exit_note=st))
    finish(out, "sociicap", ("everywhere_tags",))


if __name__ == "__main__":
    main()
