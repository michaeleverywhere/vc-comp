#!/usr/bin/env python3
"""Unshackled Ventures portfolio scraper -> unshackledventures_companies.json
Source: https://www.unshackledvc.com/portfolio — portfolio grid (JS-rendered, read via headless
Chrome): company name (card heading; the site's own "(acquired by X)" / "(NYSE: TICK)" suffix
is split into status + acquirer / ticker), Unshackled sector label, one-line description and
the card's website link."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.unshackledvc.com/portfolio"
PRIMARY = "Unshackled Ventures"
SECTOR_MAP = {"ai & enterprise": [], "climate & energy": ["Climate / Sustainability"], "consumer & e-commerce": ["Consumer"],
              "fintech": ["FinTech / Insurance"], "food & agriculture": ["CPG"], "healthcare": ["Health"],
              "space & communication": ["Deeptech / Robotics / AR/VR"], "robotics": ["Deeptech / Robotics / AR/VR"],
              "mobility": ["Transportation / Mobility"], "proptech": ["PropTech"], "education": ["Future of Work"],
              "security": ["Cybersecurity"], "developer tools": ["Dev Tools / Cloud"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=30000), "html.parser")
    out = []
    for a in s.select("a.group.relative"):
        h = a.find("h3")
        if not h:
            continue
        raw = clean(h.get_text(" ", strip=True))
        name, status, acquirer, ticker = raw, None, None, None
        m = re.match(r"^(.*?)\s*\((.+)\)\s*$", raw or "")
        if m:
            name, suf = clean(m.group(1)), m.group(2)
            ma = re.match(r"(?i)acquired by (.+)", suf)
            mt = re.match(r"^(NYSE|NASDAQ|NASDQ|TSX|LSE)\s*:\s*([A-Z.]+)$", suf.strip())
            if ma:
                status, acquirer = "Acquired", clean(ma.group(1))
            elif mt:
                status, ticker = "Public", f"{mt.group(1)}: {mt.group(2)}"
            else:
                name = raw
        ps = a.find_all("p")
        sector = clean(ps[0].get_text(" ", strip=True)) if len(ps) > 0 else None
        desc = clean(ps[1].get_text(" ", strip=True)) if len(ps) > 1 else None
        href = a.get("href") or ""
        out.append(rec(name, desc, href if href.startswith("http") and not is_social(href) else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[sector] if sector else [], sector_map=SECTOR_MAP,
                       status=status, acquirer=acquirer, ticker=ticker))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Unshackled companies")
    finish(out, "unshackledventures", ("description", "company_url", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
