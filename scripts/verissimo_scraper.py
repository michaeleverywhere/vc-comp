#!/usr/bin/env python3
"""Verissimo Ventures portfolio scraper -> verissimo_companies.json
Source: https://verissimo.vc/portfolio — a Super.so (Notion) gallery; every
/verissimo-portfolio/<slug> card links to a Notion page whose property rows give:
Founder, Invested (year -> first invested), Market, Business Model, Summary
(description), Location, Investment Stage (funding round), Website, Status
(Private / Acquired / …), Fund and Geo. Cards under "previous personal portfolio"
(partners' pre-fund angel investments) are excluded."""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://verissimo.vc/portfolio"
PRIMARY = "Verissimo Ventures"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "cyber": ["Cybersecurity"], "security": ["Cybersecurity"],
              "health": ["Health"], "healthcare": ["Health"], "devtools": ["Dev Tools / Cloud"],
              "dev tools": ["Dev Tools / Cloud"], "data": ["Data & Analytics"], "consumer": ["Consumer"]}


def props(html):
    s = BeautifulSoup(html or "", "html.parser")
    out = {}
    for p in s.select(".notion-page__property"):
        k = p.select_one(".notion-page__property-name")
        if not k:
            continue
        key = clean(k.get_text(" ", strip=True))
        w = p.select_one(".notion-page__property-name-wrapper")
        (w or k).decompose()
        pills = [clean(x.get_text(" ", strip=True)) for x in p.select(".notion-pill")]
        a = p.select_one("a[href^=http]")
        out[key] = {"pills": [x for x in pills if x],
                                                     "text": clean(p.get_text(" ", strip=True)),
                                                     "href": a["href"] if a else None}
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch_response(SOURCE_URL).content.decode("utf-8", "replace"), "html.parser")
    cards = {}
    for a in s.select("a.notion-collection-card__anchor[href]"):
        if a["href"].startswith("/verissimo-portfolio/"):
            cards.setdefault(urljoin(SOURCE_URL, a["href"]), clean(a.get_text(" ", strip=True)))
    pages = fetch_many(list(cards))
    out = []
    for url, name in cards.items():
        if not name:
            continue
        p = props(pages.get(url))
        g = lambda k: (p.get(k) or {}).get("text")
        pill = lambda k: (p.get(k) or {}).get("pills") or []
        site = (p.get("Website") or {}).get("href") or g("Website")
        if site and not site.startswith("http"):
            site = None
        inv = re.search(r"\b(19|20)\d{2}\b", g("Invested") or "")
        st = (g("Status") or "").lower()
        status = ("acquired" if "acquir" in st else "public" if ("ipo" in st or "public" in st) else
                  "closed" if ("closed" in st or "shut" in st) else "active" if st else None)
        founders = [clean(x) for x in re.split(r",|&| and ", g("Founder") or "") if clean(x)]
        out.append(rec(name, g("Summary"), site if site and not is_social(site) else None, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=pill("Market"), sector_map=SECTOR_MAP, founders=founders,
                       first_invested=int(inv.group(0)) if inv else None, business_model=g("Business Model"),
                       location=g("Location"), geo=g("Geo"), stage=", ".join(pill("Investment Stage")) or g("Investment Stage"), fund=g("Fund"),
                       portfolio_status=g("Status"), status=status, detail_url=url))
    finish(out, "verissimo", ("description", "company_url", "stage", "first_invested", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
