#!/usr/bin/env python3
"""Atlantic Labs portfolio scraper -> atlanticlabs_companies.json
Source: https://atlantic.vc/portfolio — Atlantic Labs, Berlin early-stage venture capital firm (founded by Christophe
Maire); the rendered portfolio list gives each company's name, Atlantic's one-line description, its sector label,
the firm's "(Exited)" marker and the company's atlantic.vc profile link."""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _chrome_dom import dom
from _d50_common import rec, finish

SOURCE_URL = "https://atlantic.vc/portfolio"
PRIMARY = "Atlantic Labs"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(dom(SOURCE_URL, 15000, tries=3, min_len=100000), "html.parser")
    out = []
    for a in soup.select('a[href^="/portfolio/"]'):
        n = a.select_one("p.type-m-24")
        if not n:
            continue
        raw = clean(n.get_text(" ", strip=True)) or ""
        exited = bool(re.search(r"\(Exited\)\s*$", raw))
        name = clean(re.sub(r"\s*\(Exited\)\s*$", "", raw))
        if not name:
            continue
        d = a.select_one("p.type-m-16.text-pretty")
        sec = a.select_one("div.hidden p.type-m-16") or a.select_one("p.type-eyebrow")
        sector = clean(sec.get_text(" ", strip=True)) if sec else None
        out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None, None, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=[sector] if sector else [], status="exited" if exited else "active",
                       profile_url=urljoin(SOURCE_URL, a["href"])))
    if len(out) < 80:
        raise SystemExit(f"FATAL: only {len(out)} Atlantic Labs companies")
    finish(out, "atlanticlabs", ("description", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
