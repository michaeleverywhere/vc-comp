#!/usr/bin/env python3
"""Type One Ventures portfolio scraper -> typeone_companies.json
Source: https://type1ventures.com/portfolio — the site's public Prismic content API (project
documents): company name, vertical, stage, summary, description, website and founded year."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://type1ventures.com/portfolio"
PRIMARY = "Type One Ventures"


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
    api = "https://type1ventures.cdn.prismic.io/api/v2"
    ref = next(r["ref"] for r in fetch_response(api).json()["refs"] if r.get("isMasterRef"))
    def docs(t):
        res, page = [], 1
        while True:
            j = fetch_response(f"{api}/documents/search?ref={ref}&q=%5B%5Bat(document.type,%22{t}%22)%5D%5D&pageSize=100&page={page}").json()
            res += j["results"]
            if page >= j.get("total_pages", 1):
                return res
            page += 1
    def plain(v):
        return clean(" ".join(b.get("text", "") for b in v)) if isinstance(v, list) else clean(v)
    cats = {c["id"]: plain(c["data"].get("name") or c["data"].get("title")) for c in docs("project_category")}
    for dct in docs("project"):
        x = dct["data"]
        nm = plain(x.get("name"))
        if not nm:
            continue
        cat = cats.get((x.get("category") or {}).get("id"))
        w = (x.get("website") or {}).get("url")
        out.append(rec(nm, plain(x.get("description")) or plain(x.get("summary")), w, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[cat] if cat else [], stage=clean(x.get("stage")), summary=plain(x.get("summary")),
                       year_founded=year_of(x.get("founded")), detail_url=f"https://type1ventures.com/portfolio/{dct['uid']}"))
    finish(out, "typeone", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
