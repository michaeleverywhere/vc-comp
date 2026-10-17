#!/usr/bin/env python3
"""Detroit Venture Partners portfolio scraper -> detroitvp_companies.json
Source: https://www.detroit.vc/ — homepage 'portfolio' gallery: company name
(site-authored logo alt, with 'logo' / 'tile' / 'wordmark' stripped) and website.
Tiles without alt text are skipped; the 'our mission' affiliate gallery is ignored."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.detroit.vc/"
PRIMARY = "Detroit Venture Partners"


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
    for g in s.select("div.pro-gallery"):
        h = g.find_previous(["h2", "h3", "h4"])
        if not h or txt(h).lower() != "portfolio":
            continue
        for img in g.select("img[alt]"):
            nm = clean(re.sub(r"(?i)\s*\b(logo\s*tile|logo|tile|wordmark)\b\.?\s*$", "", img.get("alt") or ""))
            nm = clean(re.sub(r"(?i)\s*\b(logo|tile)\b\.?\s*$", "", nm or ""))
            if not nm or nm.lower() in seen:
                continue
            seen.add(nm.lower())
            a = img.find_parent("a", href=True)
            out.append(rec(nm, None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "detroitvp", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
