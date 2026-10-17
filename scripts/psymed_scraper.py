#!/usr/bin/env python3
"""PsyMed Ventures portfolio scraper -> psymed_companies.json
Source: https://psymed.ventures/ — homepage portfolio: company name (link text), one-
line description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://psymed.ventures/"
PRIMARY = "PsyMed Ventures"


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
    seen = {}
    links = [a for a in s.select("a[href^='http']") if "psymed" not in a["href"] and not re.search(r"businesstrip|t\.ly|linkedin|twitter", a["href"])]
    for i, a in enumerate(links):
        t = txt(a)
        if not t or a.find("img"):
            continue
        k = re.sub(r"^https?://(www\.)?", "", a["href"]).rstrip("/").lower()
        if k in seen:
            if seen[k].get("description") is None and t != seen[k]["company_name"]:
                seen[k]["description"] = clean(t.replace("\ufeff", ""))
            continue
        t = clean(t.replace("\ufeff", ""))
        if len(t.split()) > 4 or t.upper() != t or t in ("TWITTER", "LINKEDIN"):
            continue
        r = rec(t, None, a["href"], PRIMARY, SOURCE_URL, scraped_at)
        seen[k] = r
        out.append(r)
    finish(out, "psymed", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
