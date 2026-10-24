#!/usr/bin/env python3
"""Inovia Capital portfolio scraper -> inoviacapital_companies.json
Source: https://www.inovia.vc/portfolio — Inovia Capital, Montreal-based venture and growth firm. The rendered
portfolio page embeds its company data array (name, active/exited status, "sector · stage" eyebrow, description,
year, founders, website). Entries with status "emerging" are Inovia's Emerging Managers fund commitments, not
portfolio companies, and are skipped."""
import os, sys, re, json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.inovia.vc/portfolio"
PRIMARY = "Inovia Capital"


def load():
    try:
        h = fetch(SOURCE_URL)
    except (Exception, SystemExit):  # static fetch is rate-limited (429); fall back to rendering
        h = ""
    if '{"entityId"' not in (h or ""):
        h = dom(SOURCE_URL, budget_ms=20000, min_len=50000)
    i = h.find('{"entityId"')
    if i < 0:
        raise SystemExit("FATAL: Inovia portfolio data not found")
    arr, _ = json.JSONDecoder().raw_decode(h[h.rfind("[", 0, i):])
    return arr


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for c in load():
        status = (c.get("status") or "").lower()
        if status == "emerging":
            continue
        name = clean(c.get("name"))
        if not name:
            continue
        eyebrow = clean(c.get("eyebrow")) or ""
        parts = [p.strip() for p in eyebrow.split("·")]
        sectors = [s.strip() for s in parts[0].split("/") if s.strip()] if parts and parts[0] else []
        stage = parts[1] if len(parts) > 1 and parts[1] else None
        desc = clean((c.get("desc") or "").split("\n\n")[0])
        founders = [clean(f.get("name")) for f in c.get("founders") or [] if clean(f.get("name"))]
        out.append(rec(name, desc, clean_url(c.get("website")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sectors, status="Exited" if status == "exited" else "Active",
                       stage=stage, year=c.get("year") or None, founders=founders or None))
    if len(out) < 100:
        raise SystemExit(f"FATAL: only {len(out)} Inovia companies")
    finish(out, "inoviacapital", ("description", "company_url", "status", "stage", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
