#!/usr/bin/env python3
"""Creathor Ventures portfolio scraper -> creathor_companies.json
Source: https://www.creathor.com/companies — Webflow CMS cards: company name,
location ("City/Country"), description, visible "Exit:" note when the company
has been exited, and Homepage link. Hidden (w-condition-invisible) fields are
ignored.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.creathor.com/companies"
PRIMARY = "Creathor Ventures"


def visible(el):
    return el is not None and not any("w-condition-invisible" in (p.get("class") or []) for p in [el, *el.parents] if hasattr(p, "get"))


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".item.w-dyn-item"):
            blk = it.select_one(".content-block")
            nm = blk.select_one(".investments.h3") if blk else None
            if not nm:
                continue
            loc = blk.select_one(".h5")
            desc = blk.select_one(".investments.body")
            ex = [e for e in blk.select(".exit") if visible(e) and "w-dyn-bind-empty" not in (e.get("class") or [])]
            exit_note = clean(" ".join(e.get_text(" ", strip=True) for e in ex if e.get_text(strip=True) != "Exit:")) or None
            a = blk.select_one("a.link[href^=http]")
            note = [n for n in blk.select(".investments.tiny") if visible(n) and "exit" not in (n.get("class") or [])]
            out.append(rec(nm.get_text(" ", strip=True), desc.get_text(" ", strip=True) if desc else None,
                           a["href"] if a and not is_social(a["href"]) else None, PRIMARY, SOURCE_URL, scraped_at,
                           hq_location=clean(loc.get_text(" ", strip=True).replace("/", ", ")) if loc else None,
                           exit_note=exit_note, note=clean(" ".join(n.get_text(" ", strip=True) for n in note)) or None,
                           status="exited" if exit_note else None))
    finish(out, "creathor", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
