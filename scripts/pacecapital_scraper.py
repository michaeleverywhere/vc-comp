#!/usr/bin/env python3
"""Pace Capital portfolio scraper -> pacecapital_companies.json
Source: https://www.pacecapital.com/portfolio — portfolio "balls" (JS-rendered, read via
headless Chrome): company name, Pace's one-line tagline, website link and the
"[ACQ BY X]" marker (-> status acquired + acquirer). The site prints names in capitals;
they are converted to title case (domain-style names like nexus.gg keep their suffix)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.pacecapital.com/portfolio"
PRIMARY = "Pace Capital"
NEWS = re.compile(r"/(blog|news|press)/|steampowered\.com", re.I)


def tcase(s):
    out = []
    for w in s.split():
        if w.isupper() and len(w) > 2:
            head, dot, tail = w.partition(".")
            w = head.capitalize() + (dot + tail.lower() if dot else "")
        out.append(w)
    return " ".join(out)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=20000), "html.parser")
    out = []
    for a in s.select("a[aria-label][href^=http]"):
        spans = [clean(x.get_text(" ", strip=True)) for x in a.find_all("span")]
        spans = [x for x in spans if x]
        if not spans:
            continue
        name = tcase(spans[0])
        acq = None
        rest = []
        for x in spans[1:]:
            m = re.match(r"^\[\s*ACQ\.?\s*BY\s+(.+?)\s*\]$", x, re.I)
            if m:
                acq = tcase(m.group(1))
            else:
                rest.append(x)
        desc = clean(" ".join(rest))
        if desc:
            desc = desc[:1] + desc[1:].lower()
            for k, v in (("ai", "AI"), ("llms", "LLMs"), ("3d", "3D"), ("vtubing", "VTubing")):
                desc = re.sub(rf"\b{k}\b", v, desc)
        href = a["href"]
        site = None if is_social(href) or NEWS.search(href) else href
        news = href if NEWS.search(href) and "coinbase" in href else None
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       status="acquired" if acq else "active", acquirer=acq, exit_news_url=news))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Pace companies")
    finish(out, "pacecapital", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
