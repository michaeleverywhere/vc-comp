#!/usr/bin/env python3
"""Generator Ventures portfolio scraper -> generatorvc_companies.json
Source: https://generatorvc.com/portfolio — portfolio blocks: company name (h2, '- exited'
suffix -> status), description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://generatorvc.com/portfolio"
PRIMARY = "Generator Ventures"


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
    for h in s.select("h2"):
        raw = txt(h)
        if not raw:
            continue
        ex = bool(re.search(r"(?i)\s-\s*exited\s*$", raw))
        nm = clean(re.sub(r"(?i)\s-\s*exited\s*$", "", raw))
        if nm.lower() in seen:
            continue
        p = h.find_next_sibling("p")
        if p is None:
            continue
        seen.add(nm.lower())
        a = p.find("a", href=re.compile(r"^https?://"))
        out.append(rec(nm, txt(p), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, status="exited" if ex else None))
    finish(out, "generatorvc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
