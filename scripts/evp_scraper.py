#!/usr/bin/env python3
"""Equity Venture Partners (EVP) portfolio scraper -> evp_companies.json
Source: https://www.evp.com.au/companies — Webflow list of company links plus
each company page: name, founders, EVP partner, EVP investment (round, year),
EVP fund, exit, description, website.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish, page_strings

SOURCE_URL = "https://www.evp.com.au/companies"
PRIMARY = "Equity Venture Partners"
LABELS = ("// Founder(s)", "// Investor(s)", "// EVP Investment", "// EVP Fund", "// Exit", "View jobs", "Back to companies")


def block(st, label):
    if label not in st:
        return []
    i, out = st.index(label) + 1, []
    while i < len(st) and st[i] not in LABELS:
        out.append(st[i]); i += 1
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    links = list(dict.fromkeys(urljoin(SOURCE_URL, a["href"]) for a in soup.select(".w-dyn-item a[href^='/companies/']")))
    pages = fetch_many(links, workers=6, pause=0.1)
    out = []
    for link in links:
        html = pages.get(link)
        if not html:
            continue
        st, s = page_strings(html)
        name = st[0] if st else None
        desc = None
        if "Back to companies" in st:
            i = st.index("Back to companies") + 1
            if i < len(st) and st[i] == name:
                i += 1
            if i < len(st) and len(st[i]) > 40:
                desc = st[i]
        site = None
        for a in s.select("a[href^=http]"):
            h = a["href"]
            if "evp.com.au" in h or is_social(h) or any(x in h for x in ("techcrunch", "forbes", "afr.com", "smh.com", "medium")):
                continue
            site = h; break
        inv = " ".join(block(st, "// EVP Investment")) or None
        exit_ = " ".join(block(st, "// Exit")) or None
        partner = " ".join(block(st, "// Investor(s)")) or None
        e = (exit_ or "").lower()
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, founders=block(st, "// Founder(s)"),
                       lead_partner=partner, evp_investment=inv,
                       stage=clean(re.sub(r",?\s*(19|20)\d\d$", "", inv)) if inv else None, first_invested_year=year_of(inv),
                       fund=" ".join(block(st, "// EVP Fund")) or None, exit=exit_,
                       status=("ipo" if "ipo" in e or "asx" in e else "merged" if "merger" in e else "acquired" if e else "active"), detail_url=link))
    finish(out, "evp", ("description", "company_url", "first_invested_year", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
