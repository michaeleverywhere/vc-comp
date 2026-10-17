#!/usr/bin/env python3
"""Tech Square Ventures portfolio scraper -> techsquare_companies.json
Source: https://techsquareventures.com/portfolio/ — Portfolio list: company name, founder, description,
website and fund/program group (Engage, Early Stage Fund, Exited)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://techsquareventures.com/portfolio/"
PRIMARY = "Tech Square Ventures"


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
    for it in s.select("div.eachItem"):
        nm = txt(it.select_one("p.name"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        cls = [c for c in it.get("class") or [] if c != "eachItem"]
        grp = {"engage": "Engage", "early-stage-fund": "Early Stage Fund", "exited": "Exited"}.get(cls[0] if cls else "", cls[0] if cls else None)
        ps = [txt(p) for p in it.select(".companyInfo .col p") if not (p.get("class") or [])]
        a = it.select_one("a.morecompanies[href]")
        out.append(rec(nm, ps[0] if ps else None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       founder=txt(it.select_one("p.title")), group=grp, status="exited" if grp == "Exited" else None))
    finish(out, "techsquare", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
