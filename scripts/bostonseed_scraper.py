#!/usr/bin/env python3
"""Boston Seed Capital portfolio scraper -> bostonseed_companies.json
Source: https://bostonseed.com/portfolio/ — Portfolio details: company name, founders, ticker,
description, round invested, expertise and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://bostonseed.com/portfolio/"
PRIMARY = "Boston Seed Capital"


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
    for d in s.select("div.details"):
        ab = [txt(h) for h in d.select("h6.title") if (txt(h) or "").startswith("About ")]
        if not ab:
            continue
        nm = ab[0][6:].strip()
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in d.stripped_strings if clean(x)]
        i = p.index(ab[0])
        rest = p[i + 1:]
        tk = rest[0] if rest and re.match(r"^[A-Z]{2,6}:\s*[A-Z.]+$", rest[0]) else None
        if tk:
            rest = rest[1:]
        desc = rest[0] if rest and rest[0] != "Expertise" else None
        rnd = next((x for x in rest if x.startswith("Boston Seed invested")), None)
        ex = p[p.index("Expertise") + 1] if "Expertise" in p[:-1] else None
        a = d.select_one("a[href^=http]")
        out.append(rec(nm, desc, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, ticker=tk, round=rnd,
                       sectors=[ex] if ex else [], status="public" if tk else None))
    finish(out, "bostonseed", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
