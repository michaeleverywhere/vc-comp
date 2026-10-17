#!/usr/bin/env python3
"""Highland Europe portfolio scraper -> highlandeurope_companies.json
Source: https://www.highlandeurope.com/companies/ — Companies page: company name, tagline, description,
website and exited flag."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.highlandeurope.com/companies/"
PRIMARY = "Highland Europe"


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
    for c in s.select("div.company"):
        hd = c.select_one("div.company__heading__name") or c.select_one("div.company__heading")
        raw = clean(hd.get_text(" ", strip=True)) if hd else None
        if not raw:
            continue
        ex = bool(re.search(r"\s*Exited$", raw))
        nm = re.sub(r"\s*Exited$", "", raw).strip()
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in c.stripped_strings if clean(x)]
        p = [x for x in p if x not in (raw, nm, "Exited")]
        a = [x for x in c.select("a[href^=http]") if "highlandeurope.com" not in x["href"]]
        out.append(rec(nm, p[1] if len(p) > 1 else (p[0] if p else None), site(a[0]) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       tagline=p[0] if p else None, status="exited" if ex else None))
    finish(out, "highlandeurope", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
