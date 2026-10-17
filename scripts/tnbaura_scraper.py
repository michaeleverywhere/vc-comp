#!/usr/bin/env python3
"""TNB Aura portfolio scraper -> tnbaura_companies.json
Source: https://www.tnbaura.vc/portfolio — Next.js portfolio cards: company name,
tagline and card label (Scout / Exit / M&A / Closed)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.tnbaura.vc/portfolio"
PRIMARY = "TNB Aura"


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
    for t in s.select("[id='tagline']"):
        nm = txt(t.find("h3"))
        if not nm:
            continue
        card = t.parent
        lab = card.find("div")
        lab = txt(lab) if lab is not None and lab is not t and not lab.find("h3") else None
        a = card.find_parent("a")
        ll = (lab or "").lower()
        out.append(rec(nm, txt(t.find("h4")), site(a), PRIMARY, SOURCE_URL, scraped_at, portfolio_label=lab,
                       status="exited" if ll in ("exit", "m&a") else ("closed" if ll == "closed" else None)))
    finish(out, "tnbaura", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
