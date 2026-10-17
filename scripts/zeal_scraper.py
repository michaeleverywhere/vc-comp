#!/usr/bin/env python3
"""Zeal Capital Partners portfolio scraper -> zeal_companies.json
Source: https://www.zealcapitalpartners.com/portfolio/ — portfolio flip cards: company name, status
(current/exited), description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.zealcapitalpartners.com/portfolio/"
PRIMARY = "Zeal Capital Partners"


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
    for card in s.select(".card-reveal"):
        h = card.find("h2")
        nm = txt(h)
        if not nm:
            continue
        st = txt(h.find_previous_sibling())
        d = card.select_one(".public-DraftEditor-content")
        w = next((a for a in card.find_all("a", href=True) if re.search(r"website", txt(a) or "", re.I)), None)
        stl = (st or "").lower()
        out.append(rec(nm, txt(d), site(w), PRIMARY, SOURCE_URL, scraped_at, portfolio_status=st,
                       status="exited" if "exit" in stl else ("acquired" if "acqui" in stl else None)))
    finish(out, "zeal", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
