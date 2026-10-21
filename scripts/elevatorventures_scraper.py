#!/usr/bin/env python3
"""Elevator Ventures portfolio scraper -> elevatorventures_companies.json
Source: https://www.elevator-ventures.com/portfolio — Raiffeisen Bank International's venture arm; the
portfolio page's company tiles (read via headless Chrome): company name from each tile heading, with the
site's "EXIT" prefix read as an exit and the section ("EV II portfolio companies" / "Exits of Elevator
Ventures") kept as published. The fund-of-funds section is skipped (LP stakes, not companies)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.elevator-ventures.com/portfolio"
PRIMARY = "Elevator Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=50000), "html.parser")
    out, section = [], None
    for h in s.select("h2.cmp-title__text, h3.cmp-title__text"):
        t = clean(h.get_text(" ", strip=True))
        if not t:
            continue
        if h.name == "h2":
            section = t
            continue
        if section and re.search(r"(?i)fund of funds|newsletter", section):
            continue
        exited = bool(re.match(r"(?i)^exit\b", t)) or bool(section and re.search(r"(?i)exit", section))
        name = clean(re.sub(r"(?i)^exit\s+", "", t))
        if not name:
            continue
        out.append(rec(name, None, None, PRIMARY, SOURCE_URL, scraped_at, portfolio_section=section,
                       status="acquired" if exited else "active"))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Elevator Ventures companies")
    finish(out, "elevatorventures", ("portfolio_section", "status"))


if __name__ == "__main__":
    main()
