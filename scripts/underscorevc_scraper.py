#!/usr/bin/env python3
"""Underscore VC portfolio scraper -> underscorevc_companies.json
Source: https://underscore.vc/portfolio/ — WordPress + MixItUp grid with
server-rendered lightbox panels. Each company: sector filter class on the
card, an ACQUIRED badge where applicable, and a panel with name, description,
website, Founders & Leadership, Co-Investors and an "Acquired by:" note.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://underscore.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "underscorevc_companies.json")
PRIMARY = "Underscore VC"
SECTOR_TAG_MAP = {
    "healthtech": ["Health"], "fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"],
    "cybersecurity": ["Cybersecurity"], "security": ["Cybersecurity"], "devtools": ["Dev Tools / Cloud"],
    "proptech": ["PropTech"], "logistics": ["Logistics / Supply Chain"], "supply-chain": ["Logistics / Supply Chain"],
    "edtech": ["Consumer"], "future-of-work": ["Future of Work"], "hr-tech": ["Future of Work"],
    "data": ["Data & Analytics"], "martech": ["Gaming / Media / Entertainment"], "climate": ["Climate / Sustainability"],
    "web3-blockchain": ["Web3 / Crypto"], "commerce": ["Consumer"],
}
GRID = {"col-lg-3", "col-md-4", "col-sm-6", "mix", "portfolio-spotlight"}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    filters = {}
    for f in soup.select("[data-filter]"):
        k = (f.get("data-filter") or "").lstrip(".")
        if k and k != "all":
            filters[k] = clean(f.get_text(" "))
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for card in soup.select("div.mix"):
        panel = card.select_one(".mfp-portfolio-detail")
        if not panel:
            continue
        t = panel.select_one(".mfp-portfolio__item .title")
        name = clean(t.get_text(" ")) if t else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        d = panel.select_one(".desc-big")
        desc = clean(d.get_text(" ")) if d else None
        link = panel.select_one("a.icon-link[href]")
        people = {}
        for li in panel.select(".entry-content li"):
            h = li.select_one(".position")
            if h:
                people[clean(h.get_text()).lower()] = [clean(p.get_text(" ")) for p in li.select(".users p, .users a") if clean(p.get_text(" "))]
        txt = clean(panel.select_one(".entry-content").get_text(" ")) if panel.select_one(".entry-content") else ""
        m = re.search(r"Acquired by:\s*([^.\n]+?)(?:\s{2,}|$|Related Articles)", txt or "")
        acquired = bool(card.select_one(".aquired-notice")) or bool(m)
        cats = [c for c in card.get("class") or [] if c not in GRID]
        sectors = [filters.get(c, c) for c in cats]
        founders = []
        for x in people.get("founders & leadership", []):
            if x not in founders:
                founders.append(x)
        coinv = []
        for x in people.get("co-investors", []):
            for y in re.split(r",\s*", x):
                if clean(y) and clean(y) not in coinv:
                    coinv.append(clean(y))
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": link["href"].strip() if link else None,
            "status": "acquired" if acquired else None,
            "acquirer": clean(m.group(1)) if m else None,
            "founders": founders,
            "co_investors": coinv,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, cats, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "acquirer", "founders", "co_investors", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
