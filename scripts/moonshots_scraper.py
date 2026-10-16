#!/usr/bin/env python3
"""Moonshots Capital portfolio scraper -> moonshots_companies.json
Source: https://moonshotscapital.com/portfolios/ — portfolio grid (`a.portfolio-link`):
company name, Moonshots vehicle label (e.g. Angel / Fund I), type labels
(exit / unicorn / veteran-led) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://moonshotscapital.com/portfolios/"
PRIMARY = "Moonshots Capital"


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
    for a in s.select("a.portfolio-link"):
        nm = txt(a.select_one(".portfolio-info-footer-title"))
        if not nm:
            continue
        # exit notes are appended to the title, e.g. "Literati Acquired by Trustbridge Partners"
        note = None
        m = re.search(r"\s+((?:Acquired by|Merged with|IPO)\b.*)$", nm)
        if m:
            nm, note = clean(nm[:m.start()]), clean(m.group(1))
        lab = txt(a.select_one(".portfolio-info-header-type"))
        exited = bool(note) or bool(lab and "exit" in lab.lower())
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at,
                       fund=txt(a.select_one(".featured-portfolio-hover--categories")), labels=lab, exit_note=note,
                       status=("acquired" if note and note.lower().startswith(("acquired", "merged")) else "exited") if exited else None))
    finish(out, "moonshots", ("company_url", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
