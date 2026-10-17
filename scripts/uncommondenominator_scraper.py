#!/usr/bin/env python3
"""Uncommon Denominator portfolio scraper -> uncommondenominator_companies.json
Source: https://www.uncommonvc.com/ — homepage investments logo grid: company
names from logo alt text ("Logo" / "Portfolio:" wording stripped; non-name alts skipped)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.uncommonvc.com/"
PRIMARY = "Uncommon Denominator"


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
    for img in s.find_all("img"):
        a = img.find_parent("a")
        if a and "uncommonvc.com/" in (a.get("href") or "") and a.get("href") != "https://www.uncommonvc.com/":
            break  # team section starts (team members link to their bio pages)
        if a:
            continue
        al = clean(img.get("alt")) or ""
        al = re.sub(r"^(Portfolio:\s*|Logo of\s+)", "", al)
        al = re.sub(r"([\s_-]*Logo([\s_-]*Color)?)$", "", al, flags=re.I)
        al = clean(al)
        if not al or len(al) < 2 or al.lower() == "logo" or "honig" in al.lower() or re.search(r"[ÃÂâ]", al):
            continue
        out.append(rec(al, None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "uncommondenominator", ("everywhere_tags",))


if __name__ == "__main__":
    main()
