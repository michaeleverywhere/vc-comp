#!/usr/bin/env python3
"""Conviction portfolio scraper -> conviction_companies.json
Source: https://www.conviction.com/ — "Portfolio" list: company name + website
and founders ("<Company>, founded by ..."). Site publishes no descriptions.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.conviction.com/"
PRIMARY = "Conviction"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for li in soup.select("li"):
        txt = clean(li.get_text(" ", strip=True)) or ""
        if "founded by" not in txt:
            continue
        links = li.select("a[href^=http]")
        co = next((a for a in links if not is_social(a["href"])), None)
        name = clean(co.get_text(" ", strip=True)) if co else clean(txt.split(",")[0])
        tail = txt.split("founded by", 1)[1]
        founders = [clean(x) for x in re.split(r",|\band\b", tail) if clean(x)]
        out.append(rec(name, None, co["href"] if co else None, PRIMARY, SOURCE_URL, scraped_at, founders=founders))
    finish(out, "conviction", ("company_url", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
