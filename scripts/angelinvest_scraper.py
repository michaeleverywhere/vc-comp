#!/usr/bin/env python3
"""Angel Invest portfolio scraper -> angelinvest_companies.json
Source: https://angelinvest.ventures/portfolio — the firm's portfolio highlights
(server-rendered list of /portfolio/<slug> pages). Each company page gives name,
location, description, Angel Invest sector label, website, founders (name + role),
the Angel Invest partner on the deal and named co-investors."""
import os, re, sys, time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://angelinvest.ventures/portfolio"
PRIMARY = "Angel Invest"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"], "healthtech": ["Health"],
              "health": ["Health"], "climate": ["Climate / Sustainability"], "climatetech": ["Climate / Sustainability"],
              "proptech": ["PropTech"], "deeptech": ["Deeptech / Robotics / AR/VR"], "mobility": ["Transportation / Mobility"],
              "cybersecurity": ["Cybersecurity"], "devtools": ["Dev Tools / Cloud"], "dev tools": ["Dev Tools / Cloud"],
              "hr tech": ["Future of Work"], "future of work": ["Future of Work"], "web3": ["Web3 / Crypto"],
              "gaming": ["Gaming / Media / Entertainment"], "logistics": ["Logistics / Supply Chain"],
              "consumer": ["Consumer"], "legaltech": ["RegTech/Gov/Legal"]}


def page(url):
    b = BeautifulSoup(fetch(url), "html.parser")
    for t in b(["script", "style", "svg", "nav", "header", "footer"]):
        t.decompose()
    strs = [clean(x) for x in b.stripped_strings if clean(x)]
    h1 = b.select_one("h1")
    name = clean(h1.get_text(" ", strip=True)) if h1 else None
    d = {"name": name}
    if name and name in strs:
        i = strs.index(name, 1) if strs.count(name) > 1 else strs.index(name)
        rest = strs[i + 1:]
        if rest:
            d["location"] = rest[0]
        try:
            fi = rest.index("Founders")
        except ValueError:
            fi = None
        if fi:
            body = rest[1:fi]
            d["sector"] = body[-1] if len(body) >= 2 and len(body[-1]) < 40 else None
            d["description"] = " ".join(x for x in body if x != d.get("sector")) or None
            ti = rest.index("Angel Invest Team") if "Angel Invest Team" in rest else len(rest)
            ppl = rest[fi + 1:ti]
            d["founders"] = [f"{ppl[k]} ({ppl[k + 1]})" for k in range(0, len(ppl) - 1, 2)]
            ci = rest.index("Co-Investors") if "Co-Investors" in rest else None
            team = rest[ti + 1:ci] if ci else rest[ti + 1:ti + 3]
            d["partner"] = team[0] if team else None
    co, web = [], None
    for a in b.select("a[href^=http]"):
        h = a["href"].strip()
        if is_social(h) or "angelinvest.ventures" in h or "airtable.com" in h or "crunchbase" in h:
            continue
        if web is None:
            web = h
        else:
            img = a.find("img")
            alt = clean(img.get("alt")) if img else None
            alt = re.sub(r"\s*logo$", "", alt, flags=re.I) if alt else None
            co.append(clean(a.get_text(" ", strip=True)) or alt or re.sub(r"^www\.", "", urlparse(h).netloc))
    d["website"], d["co_investors"] = web, [c for c in co if c]
    return d


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    slugs = list(dict.fromkeys(a["href"].split("?")[0] for a in s.select('a[href^="/portfolio/"]')))
    out = []
    for sl in slugs:
        d = page(urljoin(SOURCE_URL, sl)); time.sleep(0.2)
        if not d.get("name"):
            continue
        sec = d.get("sector")
        out.append(rec(d["name"], d.get("description"), d.get("website"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sec] if sec else [], sector_map=SECTOR_MAP, sector_label=sec,
                       location=d.get("location"), founders=d.get("founders") or [],
                       angel_invest_partner=d.get("partner"), co_investors=d.get("co_investors") or [],
                       profile_url=urljoin(SOURCE_URL, sl)))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Angel Invest companies")
    finish(out, "angelinvest", ("description", "company_url", "location", "sector_label", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
