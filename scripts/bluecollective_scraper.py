#!/usr/bin/env python3
"""Blue Collective portfolio scraper -> bluecollective_companies.json
Source: https://bluecollective.com/portfolio/ — Portfolio list: company name, website, founders and
investment year."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://bluecollective.com/portfolio/"
PRIMARY = "Blue Collective"


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
    for it in s.select("div.layer-content"):
        ps = it.select("p")
        first = next((p for p in ps if txt(p)), None)
        if not first or re.match(r"(founders?|invested)\b", txt(first), re.I):
            continue
        a = next((x for x in first.select("a[href]") if not re.search(r"crunchbase|linkedin|twitter|x\.com", x["href"])), None)
        nm = txt(a) if a else clean(next(iter(first.stripped_strings), ""))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        t = [txt(p) for p in ps if txt(p)]
        fo = next((x.split(":", 1)[1].strip() for x in t if x.lower().startswith("founder")), None)
        yr = next((x.split(":", 1)[1].strip() for x in t if x.lower().startswith("invested")), None)
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, founders=fo, invested_year=yr))
    finish(out, "bluecollective", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
