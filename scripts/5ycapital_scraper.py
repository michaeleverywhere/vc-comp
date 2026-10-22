#!/usr/bin/env python3
"""5Y Capital portfolio scraper -> 5ycapital_companies.json
Source: https://www.5ycap.com/en/portfolio — Shanghai/Beijing venture firm (formerly Morningside Venture Capital,
not the separately tracked Morningside Group); static English portfolio page listing each company as a linked name
(company website), with the stock ticker/exchange in brackets for listed companies (kept as `ticker`)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.5ycap.com/en/portfolio"
PRIMARY = "5Y Capital"
TICK = re.compile(r"\s*[（(]\s*([^()（）]*(?:NASDAQ|NYSE|\.HK|\.SZ|\.SH|HKEX|SSE|SZSE)[^()（）]*)\s*[)）]\s*$", re.I)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select(".text_link_list li a[href]"):
        raw = clean(a.get_text(" ", strip=True))
        if not raw:
            continue
        m = TICK.search(raw)
        name = clean(raw[:m.start()]) if m else raw
        ticker = clean(m.group(1)) if m else None
        out.append(rec(name, None, a["href"], PRIMARY, SOURCE_URL, scraped_at, ticker=ticker))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} 5Y Capital companies")
    finish(out, "5ycapital", ("company_url", "ticker", "everywhere_tags"))


if __name__ == "__main__":
    main()
