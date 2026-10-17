#!/usr/bin/env python3
"""Adapt Ventures portfolio scraper -> adaptvc_companies.json
Source: https://adaptvc.com/companies — Framer portfolio cards: company name,
one-line description, HQ, stage invested, current stage."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://adaptvc.com/companies"
PRIMARY = "Adapt Ventures"


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
    for it in s.select("div[class*=framer-v8hmmi]"):
        card = it.find_parent(attrs={"data-highlight": "true"}) or it.parent
        ps = [txt(p) for p in it.select("p.framer-text") if txt(p)]
        if not ps:
            continue
        nm = ps[0]
        if nm.lower() in seen:
            continue
        seen.add(nm.lower())
        kv, last = {}, None
        for p in card.find_parent().select("p.framer-text") if card.find_parent() else []:
            t = txt(p)
            if t and t.endswith(":"):
                last = t[:-1]
            elif t and last:
                kv[last] = t; last = None
        out.append(rec(nm, ps[1] if len(ps) > 1 else None, None, PRIMARY, SOURCE_URL, scraped_at, headquarters=kv.get("Based"),
                       stage_invested=kv.get("Invested in"), stage=kv.get("Current stage")))
    finish(out, "adaptvc", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
