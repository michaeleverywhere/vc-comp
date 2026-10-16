#!/usr/bin/env python3
"""ZhenFund (真格基金) portfolio scraper -> zhenfund_companies.json
Source: https://www.zhenfund.com/portfolio — server-rendered list; each <li> has
the company name and a popup with ZhenFund's Chinese-language company introduction
(公司介绍) and the official website link. Names/descriptions kept as published.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.zhenfund.com/portfolio"
PRIMARY = "ZhenFund"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch_response(SOURCE_URL).content, "html.parser")
    out = []
    for li in soup.select("li[data-id]"):
        n = li.select_one(".intro_1") or li.select_one(".popupContent .title")
        if not n:
            continue
        name = clean(n.get_text(" ", strip=True))
        desc = None
        for p in li.select(".leftpart p"):
            t = clean(p.get_text(" ", strip=True)) or ""
            if t.startswith("公司介绍"):
                desc = clean(t.split("：", 1)[-1].split(":", 1)[-1])
                break
        a = li.select_one(".rightpart a.button[href^=http]")
        out.append(rec(name, desc, a["href"] if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "zhenfund", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
