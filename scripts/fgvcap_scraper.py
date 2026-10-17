#!/usr/bin/env python3
"""FGV Capital portfolio scraper -> fgvcap_companies.json
Source: https://fgv.vc/portfolio — portfolio table: company name (h5), one-line
description, sector and location."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://fgv.vc/portfolio"
PRIMARY = "FGV Capital"


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
    for h in s.select("h5"):
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        row = h.parent.parent.parent
        ss = [clean(x) for x in row.stripped_strings if clean(x)]
        if len(ss) < 3 or ss[0] != nm:
            continue
        seen.add(nm.lower())
        a = row.find("a", href=re.compile(r"^https?://(?!(www\.)?fgv\.)"))
        out.append(rec(nm, ss[1], site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, sector=ss[2] if len(ss) > 2 else None,
                       location=ss[3] if len(ss) > 3 else None))
    finish(out, "fgvcap", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
