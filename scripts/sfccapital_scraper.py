#!/usr/bin/env python3
"""SFC Capital portfolio scraper -> sfccapital_companies.json
Source: https://www.sfccapital.com/portfolio — SFC Capital, London-based seed-stage venture investor (SEIS/EIS funds),
one of the UK's most active early-stage investors. Each portfolio card gives the company name, one-line description,
website, sector category (B2B Software, B2C Tech, Consumer Products, FinTech, Green, Hardware & Robotics, Health)
and an exit badge (Full Exit / Partial Exit) where applicable."""
import os, sys, re, html as _h
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.sfccapital.com/portfolio"
PRIMARY = "SFC Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cats = {}
    for inp in soup.select("input.post-category[data-filter]"):
        sp = inp.find_next("span")
        if sp:
            cats[inp["data-filter"].lstrip(".")] = clean(_h.unescape(sp.get_text()))
    out, seen = [], set()
    for card in soup.select("div.oportfolio-cols.element-item"):
        a = card.select_one(".blcolstitle h5 a") or card.select_one(".blcolstitle h5")
        name = clean(a.get_text(" ")) if a else None
        if not name:
            img = card.select_one(".blcolsimg img[alt]")
            name = clean(re.sub(r"\s+logo$", "", img["alt"], flags=re.I)) if img else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        classes = card.get("class") or []
        sectors = [cats[c] for c in classes if c in cats and c != "exited_startups"] or None
        badge = card.select_one(".portfolio-exit-badge__label")
        exit_label = clean(badge.get_text(" ")) if badge else None
        txt = card.select_one(".blcolstxt")
        site = a.get("href") if a is not None and a.name == "a" else None
        if not site:
            b = card.select_one(".blcolsbtn a[href]")
            site = b["href"] if b else None
        sid = card.select_one("input.startup_id")
        out.append(rec(name, clean(txt.get_text(" ")) if txt else None, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sectors, status="Exited" if exit_label else "Active", exit_type=exit_label,
                       sfc_startup_id=sid.get("value") if sid else None))
    if len(out) < 200:
        raise SystemExit(f"FATAL: only {len(out)} SFC Capital companies")
    finish(out, "sfccapital", ("description", "website", "everywhere_tags"))


if __name__ == "__main__":
    main()
