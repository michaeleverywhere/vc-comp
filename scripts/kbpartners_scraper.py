#!/usr/bin/env python3
"""KB Partners portfolio scraper -> kbpartners_companies.json
Source: https://kbpartners.com/portfolio/ — server-rendered WordPress portfolio grid: one item per
company with the site's own data attributes (company name, website, KB fund, exit tag) plus the
Current / Past filter class, the card description and the published exit note (e.g. "Acquired by ...")."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://kbpartners.com/portfolio/"
PRIMARY = "KB Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in s.select("div.kbp-company-item"):
        name = clean(it.get("data-title"))
        if not name:
            continue
        cls = it.get("class") or []
        tag = clean(it.get("data-tag"))
        d = it.select_one("div.kbp-company-description")
        paras = [clean(p.get_text(" ", strip=True)) for p in d.select("p")] if d else []
        paras = [p for p in paras if p]
        note = None
        strong = d.select_one("strong") if d else None
        if strong:
            note = clean(strong.get_text(" ", strip=True))
        desc = next((p for p in paras if p != note), None)
        if not note and len(paras) > 1:
            note = paras[-1]
        past = "past" in cls
        if past and (tag in ("Acquired", "IPO") or (note and any(w in note.lower() for w in ("acquired", "merged", "publicly-traded", "nasdaq", "nyse")))):
            status = "acquired" if tag != "IPO" else "ipo"
        elif past:
            status = "past"
        else:
            status = "active"
        out.append(rec(name, desc, it.get("data-website"), PRIMARY, SOURCE_URL, scraped_at,
                       kb_fund=clean(it.get("data-fund")), exit_type=tag, exit_note=note,
                       portfolio_bucket="Past" if past else "Current", status=status))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} KB Partners companies")
    finish(out, "kbpartners", ("description", "company_url", "kb_fund", "exit_note", "everywhere_tags"))


if __name__ == "__main__":
    main()
