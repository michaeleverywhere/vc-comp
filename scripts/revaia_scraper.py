#!/usr/bin/env python3
"""Revaia portfolio scraper -> revaia_companies.json
Source: https://www.revaia.com/portfolio — Revaia, Paris growth-stage venture capital firm; the rendered portfolio
cards give each company's name, Revaia's one-line description, website and Revaia's own note on the round it
joined (e.g. "Revaia led Semble's €35M Series C"), from which the round label, size and Revaia's role are read."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, clean_url
from _chrome_dom import dom
from _d50_common import rec, finish

SOURCE_URL = "https://www.revaia.com/portfolio"
PRIMARY = "Revaia"
CUR = {"€": "EUR", "$": "USD", "£": "GBP"}


def parse_round(note):
    if not note:
        return {}
    st = re.search(r"\b(Pre-Seed|Seed|Series [A-H])\b", note, re.I)
    amt = re.search(r"([€$£])\s?(\d+(?:\.\d+)?)\s?([MmBb])\b", note)
    role = re.match(r"Revaia (co-led|led|invested in|took part in)", note, re.I)
    out = {"investment_stage": st.group(1).title().replace("Pre-Seed", "Pre-Seed") if st else None,
           "revaia_role": role.group(1).lower() if role else None}
    if amt:
        mult = 1_000_000 if amt.group(3).lower() == "m" else 1_000_000_000
        out["revaia_round_amount"] = int(float(amt.group(2)) * mult)
        out["revaia_round_currency"] = CUR[amt.group(1)]
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(dom(SOURCE_URL, 15000, tries=3, min_len=100000), "html.parser")
    out = []
    for d in soup.select("div.my-details"):
        n = d.select_one("h2.my-name")
        name = clean(n.get_text(" ", strip=True)) if n else None
        if not name:
            continue
        desc = d.select_one("p.my-description")
        note = clean(d.select_one("div.my-round").get_text(" ", strip=True)) if d.select_one("div.my-round") else None
        a = d.select_one("a.my-link[href]")
        out.append(rec(name, clean(desc.get_text(" ", strip=True)) if desc else None,
                       clean_url(a["href"]) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       revaia_round_note=note, **parse_round(note)))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Revaia companies")
    finish(out, "revaia", ("description", "company_url", "investment_stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
