#!/usr/bin/env python3
"""iSelect Fund portfolio scraper -> iselectfund_companies.json
Source: https://www.iselectfund.com/portfolio-companies/ — portfolio table: company name (link text),
website, year established, location and prior funding round."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.iselectfund.com/portfolio-companies/"
PRIMARY = "iSelect Fund"


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
    for c in s.select("div.compName"):
        a = c.find("a", href=re.compile(r"^https?://"))
        nm = txt(a)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        info = c.select_one(".compInfo")
        t = info.get_text("\n", strip=True) if info else ""
        f = dict((m.group(1).strip().lower(), clean(m.group(2))) for m in re.finditer(r"([A-Za-z ]+):\s*\n?([^\n]+)", t))
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, year=year_of(f.get("established") or ""),
                       location=f.get("location"), stage=f.get("prior round funding")))
    finish(out, "iselectfund", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
