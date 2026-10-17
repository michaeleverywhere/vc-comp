#!/usr/bin/env python3
"""Deviation Capital portfolio scraper -> deviation_companies.json
Source: https://deviation.com/ — the homepage 'Companies' list (the full list is embedded in
the Next.js page data: name, website when given). '(acq: X)' suffixes become status=exited
with the acquirer kept in exit_note. Names only; no descriptions on the site.
"""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://deviation.com/"
PRIMARY = "Deviation Capital"



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
    out, seen = [], set()
    t = fetch_response(SOURCE_URL).content.decode("utf-8", "replace").replace('\\"', '"')
    pat = r'\{"_id":"([0-9a-f-]{36})","featuredLogo":(?:null|\{.*?\}),"name":"([^"]+)","showOnMainPage":(?:true|false),"website":(null|"[^"]*")\}'
    for cid, nm, web in re.findall(pat, t):
        if cid in seen:
            continue
        seen.add(cid)
        nm = clean(nm)
        acq = None
        m = re.match(r"^(.*?)\s*\(acq:\s*([^)]+)\)\s*$", nm)
        if m:
            nm, acq = clean(m.group(1)), clean(m.group(2))
        web = web.strip('"') if web != "null" else None
        web = web if web and web.startswith("http") and not is_social(web) else None
        out.append(rec(nm, None, web, PRIMARY, SOURCE_URL, scraped_at,
                       status="exited" if acq else None, exit_note=("Acquired by " + acq) if acq else None))
    finish(out, "deviation", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
