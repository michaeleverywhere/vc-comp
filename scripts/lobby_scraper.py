#!/usr/bin/env python3
"""Lobby Capital portfolio scraper -> lobby_companies.json
Source: https://lobby.vc/portfolio/ — Elementor investment cards: name, status,
sector, sub-sector, location, investment lead, about text and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://lobby.vc/portfolio/"
PRIMARY = "Lobby Capital"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    labels = {"Status:", "Sector:", "Sub‑Sector:", "Sub-Sector:", "Location:", "Investment Lead:", "About:"}
    for it in s.select(".past-investment-item"):
        parts = [clean(x) for x in it.stripped_strings if clean(x)]
        if not parts or parts[0] in labels:
            continue
        nm, f, cur = parts[0], {}, None
        for p in parts[1:]:
            if p in labels:
                cur = p.rstrip(":").replace("‑", "-")
                f[cur] = []
            elif cur:
                f[cur].append(p)
        g = lambda k: clean(" ".join(f.get(k, [])).replace(" / ", " / ")) or None
        st = g("Status") or ""
        out.append(rec(nm, g("About"), site(it.select_one("a[href^='http']")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x for x in (g("Sector"), g("Sub-Sector")) if x], location=g("Location"), investment_lead=g("Investment Lead"),
                       portfolio_status=st or None, status="exited" if st.lower().startswith("exit") else ("active" if st.lower().startswith("active") else None)))
    finish(out, "lobby", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
