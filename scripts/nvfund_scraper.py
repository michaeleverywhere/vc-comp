#!/usr/bin/env python3
"""Novartis Venture Fund portfolio scraper -> nvfund_companies.json
Source: https://www.nvfund.com/portfolio — "Our Portfolio Investments" cards
(name + company page) and each company page: NVF board representatives,
therapeutic area, location, description and website ("Visit <name>").
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean
from _d50_common import rec, finish, page_strings

ORIGIN = "https://www.nvfund.com"
SOURCE_URL = ORIGIN + "/portfolio"
PRIMARY = "Novartis Venture Fund"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch_response(SOURCE_URL).content, "html.parser")
    cards = {}
    for a in soup.select('a[href^="/portfolio/"]'):
        h = a.find("h3")
        if h and clean(h.get_text()):
            cards.setdefault(ORIGIN + a["href"], clean(h.get_text(" ", strip=True)))
    pages = fetch_many(list(cards), workers=6, pause=0.1)
    out = []
    for url, name in cards.items():
        st, ds = page_strings(pages.get(url) or "")
        vi = next((i for i, t in enumerate(st) if t.startswith("Visit ")), None)
        site = next((a["href"] for a in ds.select("a[href^=http]") if clean(a.get_text()).startswith("Visit ")), None)
        desc = loc = area = None
        board = []
        if name in st:
            ni = st.index(name)
            end = vi if vi is not None else len(st)
            body = st[ni + 1:end]
            for j, t in enumerate(body):
                if t.startswith("- ") and j > 0:
                    board.append(f"{body[j - 1]} ({t[2:].strip()})")
            tail = [t for j, t in enumerate(body) if not t.startswith("- ") and not (j + 1 < len(body) and body[j + 1].startswith("- "))]
            if tail:
                desc = tail[-1] if len(tail[-1]) > 30 else None
                rest = tail[:-1] if desc else tail
                if rest:
                    loc = rest[-1]
                if len(rest) > 1:
                    area = rest[-2]
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, sectors=[area] if area else None,
                       location=loc, board_members=", ".join(board) or None, detail_url=url))
    finish(out, "nvfund", ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
