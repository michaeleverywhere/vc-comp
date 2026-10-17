#!/usr/bin/env python3
"""August Capital portfolio scraper -> augustcap_companies.json
Source: https://www.augustcap.com/portfolio/active-funds/ — portfolio tooltips: company name
(bold label, '(acquired by X)' split into exit note), description, industry
sector, headquarters and lead investment professional."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.augustcap.com/portfolio/active-funds/"
PRIMARY = "August Capital"


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
    for box in s.select("div.port-tooltip-text-content-inner"):
        f = {}
        main = None
        for p in box.find_all("p"):
            st = p.find("strong")
            if not st:
                continue
            k = txt(st)
            v = clean(p.get_text(" ", strip=True)[len(st.get_text(" ", strip=True)):].lstrip(" :"))
            if k in ("Industry Sector", "Headquartered", "Lead Investment Professional"):
                f[k] = v
            else:
                main = (k, v)
        if not main:
            continue
        raw, d = main
        m = re.search(r"\s*\((acquired by[^)]*|ipo[^)]*|merged[^)]*)\)\s*$", raw, re.I)
        nm = clean(raw[: m.start()]) if m else clean(raw)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        out.append(rec(nm, d or None, None, PRIMARY, SOURCE_URL, scraped_at, sector=f.get("Industry Sector"),
                       location=f.get("Headquartered"), lead_partner=f.get("Lead Investment Professional"),
                       status="exited" if m else None, exit_note=m.group(1) if m else None))
    finish(out, "augustcap", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
