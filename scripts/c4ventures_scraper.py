#!/usr/bin/env python3
"""C4 Ventures portfolio scraper -> c4ventures_companies.json
Source: https://c4v.com/companies/ — WordPress REST company records: company name,
first paragraph of the site's write-up, fund, location, sector, theme and status taxonomies."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://c4v.com/companies/"
PRIMARY = "C4 Ventures"


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
    from _d50_common import wp_all, wp_terms
    from _scraper_common import html_text
    origin = "https://c4v.com"
    tax = {k: wp_terms(origin, k) for k in ("fund-company", "location-company", "sector-company", "status-company", "theme-company")}
    names = lambda p, k: [tax[k].get(i) for i in (p.get(k) or []) if tax[k].get(i)]
    for p in wp_all(origin, "company"):
        nm = html_text(p["title"]["rendered"])
        if not nm:
            continue
        paras = re.findall(r"<p[^>]*>(.*?)</p>", p.get("content", {}).get("rendered", ""), re.S)
        desc = next((html_text(x) for x in paras if html_text(x)), None)
        st = names(p, "status-company")
        out.append(rec(nm, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=names(p, "sector-company") + names(p, "theme-company"),
                       fund=", ".join(names(p, "fund-company")) or None, location=", ".join(names(p, "location-company")) or None,
                       portfolio_status=", ".join(st) or None, status="exited" if any("exit" in x.lower() for x in st) else None,
                       detail_url=p.get("link")))
    finish(out, "c4ventures", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
