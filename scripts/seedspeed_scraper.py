#!/usr/bin/env python3
"""seed + speed Ventures portfolio scraper -> seedspeed_companies.json
Source: https://www.seedandspeed.com/portfolio — Webflow portfolio cards: company name (logo alt
text), one-liner, year, stage, sector and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.seedandspeed.com/portfolio"
PRIMARY = "seed + speed Ventures"


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
    for c in s.select("div.portfolio-card"):
        img = c.select_one("img[alt]")
        nm = clean(re.sub(r"\s*logo$", "", img.get("alt") or "", flags=re.I)) if img else None
        if not nm:
            continue
        tags = [txt(x) for x in c.select(".portfolio-tag") if txt(x)]
        yr = next((t for t in tags if re.fullmatch(r"(19|20)\d\d", t)), None)
        rest = [t for t in tags if t != yr]
        a = c.select_one("a[href]")
        out.append(rec(nm, txt(c.select_one(".portfolio-card-oneliner")), None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=rest[1:], vintage_year=yr, stage=rest[0] if rest else None,
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "seedspeed", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
