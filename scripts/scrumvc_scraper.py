#!/usr/bin/env python3
"""Scrum Ventures portfolio scraper -> scrumvc_companies.json
Source: https://scrum.vc/investment/ — portfolio grid (`li.portfolio-item`)
under Featured / IPO / M&A / Portfolio headings: company name (site-authored
logo alt) and profile link; IPO and M&A sections are marked exited."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://scrum.vc/investment/"
PRIMARY = "Scrum Ventures"


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
    for li in s.select("li.portfolio-item"):
        img = li.select_one("img[alt]")
        nm = clean(img.get("alt")) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        h = li.find_previous("h2", class_="small")
        sec = txt(h)
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, profile_url=li.get("data-href"),
                       status="exited" if sec in ("IPO", "M&A") else None, exit_type=sec if sec in ("IPO", "M&A") else None))
    finish(out, "scrumvc", ("everywhere_tags",))


if __name__ == "__main__":
    main()
