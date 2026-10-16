#!/usr/bin/env python3
"""Supernode Ventures portfolio scraper -> supernode_companies.json
Source: https://www.supernode.vc/portfolio — Squarespace list: company name (bold
lead), description, rounds invested and current stage."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.supernode.vc/portfolio"
PRIMARY = "Supernode Ventures"


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
    for li in s.select("li.list-item"):
        ps = li.select(".list-item-content__description p")
        if not ps or not ps[0].find("strong"):
            continue
        st = ps[0].find("strong")
        nm = txt(st) or ""
        after = st.next_sibling if st else None
        if nm.endswith(" i") and isinstance(after, str) and after.startswith("s "):
            nm = nm[:-2]  # bold run swallowed the "i" of "is" ("by Humankind i" + "s a ...")
        m = re.search(r"\s*\((acquired|closed|exited)\)\s*$", nm, flags=re.I)
        flag = m.group(1).lower() if m else None
        nm = clean(nm[:m.start()] if m else nm)
        if not nm:
            continue
        info = {}
        for p in ps[1:]:
            st = p.find("strong")
            if st and txt(st):
                k = txt(st).rstrip(":")
                info[k] = clean(p.get_text(" ", strip=True)[len(st.get_text(" ", strip=True)):])
        out.append(rec(nm, txt(ps[0]), None, PRIMARY, SOURCE_URL, scraped_at, rounds_invested=info.get("Round Invested"),
                       stage=info.get("Current Stage"),
                       status=flag))
    finish(out, "supernode", ("description", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
