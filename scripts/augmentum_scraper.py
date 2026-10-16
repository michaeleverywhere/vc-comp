#!/usr/bin/env python3
"""Augmentum Fintech portfolio scraper -> augmentum_companies.json
Source: https://augmentum.vc/ — WP REST `portfolio` posts: name and the firm's
write-up (first paragraph = description; full text kept as investment_note,
which often states Augmentum's round and amount) plus the website link from
each company page.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_many, html_text, clean, is_social
from _d50_common import rec, finish, wp_all

ORIGIN = "https://augmentum.vc"
SOURCE_URL = "https://augmentum.vc/our-portfolio/"
PRIMARY = "Augmentum Fintech"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "portfolio")
    pages = fetch_many([p["link"] for p in posts], workers=6, pause=0.1)
    out = []
    for p in posts:
        cs = BeautifulSoup(p["content"]["rendered"] or "", "html.parser")
        paras = [clean(x.get_text(" ", strip=True)) for x in cs.select("p")]
        paras = [x for x in paras if x]
        site = None
        ds = BeautifulSoup(pages.get(p["link"]) or "", "html.parser")
        for a in ds.select("a[href^=http]"):
            h = a["href"]
            t = clean(a.get_text(" ", strip=True)) or ""
            host = urlparse(h).netloc.replace("www.", "")
            if "augmentum" in h or is_social(h) or not host:
                continue
            if host and host.split(".")[0] in t.lower():
                site = h
                break
        out.append(rec(html_text(p["title"]["rendered"]), paras[0] if paras else None, site, PRIMARY, SOURCE_URL,
                       scraped_at, investment_note=" ".join(paras[1:]) or None,
                       status="exited" if any("exit" in c for c in p.get("class_list") or []) else None))
    finish(out, "augmentum", ("description", "company_url", "investment_note", "everywhere_tags"))


if __name__ == "__main__":
    main()
