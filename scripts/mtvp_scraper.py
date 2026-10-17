#!/usr/bin/env python3
"""Millennium Technology Value Partners (MTVP) portfolio scraper -> mtvp_companies.json
Source: https://mtvlp.com/portfolio/ — WordPress flip-card gallery: company name (h4),
one-line description, exit note ("Acquired by X in YYYY" / IPO), website ("Learn more")
and the card's filter classes (ai/enterprise/consumer/infrastructure/fintech/mobility,
plus "exit") used as firm sectors."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://mtvlp.com/portfolio/"
PRIMARY = "Millennium Technology Value Partners"
LABELS = {"ai": "AI", "enterprise": "Enterprise", "consumer": "Consumer", "infrastructure": "Infrastructure",
          "fintech": "Fintech", "mobility": "Mobility"}
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "mobility": ["Transportation / Mobility"],
              "infrastructure": ["Dev Tools / Cloud"], "consumer": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch_response(SOURCE_URL).content.decode("utf-8", "replace"), "html.parser")
    out = []
    for card in s.select("div.flip-card"):
        back = card.select_one(".flip-card-back")
        h = back.select_one("h4") if back else None
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        st = back.select_one(".portfolio_status2")
        note = clean(st.get_text(" ", strip=True)) if st else None
        if st:
            st.decompose()
        a = back.select_one("a[href]")
        href = (a.get("href") or "").strip() if a else ""
        if a:
            a.decompose()
        h.decompose()
        desc = clean(back.get_text(" ", strip=True))
        cls = card.get("class") or []
        sectors = [LABELS[c] for c in cls if c in LABELS]
        exited = "exit" in cls
        status = None
        if note and re.search(r"acquired|merged", note, re.I):
            status = "acquired"
        elif note and re.search(r"\bIPO\b|NASDAQ|NYSE|public|listed", note, re.I):
            status = "public"
        elif exited:
            status = "exited"
        else:
            status = "active"
        y = re.search(r"\b(19|20)\d{2}\b", note or "")
        out.append(rec(name, desc, href if href.startswith("http") and not is_social(href) else None, PRIMARY,
                       SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP, exit_note=note,
                       exit_year=int(y.group(0)) if y else None, status=status))
    finish(out, "mtvp", ("description", "company_url", "exit_note", "everywhere_tags"))


if __name__ == "__main__":
    main()
