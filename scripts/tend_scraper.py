#!/usr/bin/env python3
"""10D portfolio scraper -> tend_companies.json
Sources: WP REST `investments` (all names + `industries` taxonomy) and the
https://www.10d.vc/portfolio/ cards (industry, description, website), matched
to names by description lead / website domain.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlparse
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, html_text
from _d50_common import rec, finish, wp_all, wp_terms

ORIGIN = "https://www.10d.vc"
SOURCE_URL = "https://www.10d.vc/portfolio/"
PRIMARY = "10D"
ALIASES = {"c* health": "c8health"}  # site renders the name with an asterisk


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "investments")
    inds = wp_terms(ORIGIN, "industries")
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = []
    for li in soup.select("li:has(p.description)"):
        a = li.select_one("a[href]")
        ind = li.select_one("p.industry strong")
        d = li.select_one("p.description")
        cards.append({"url": a["href"] if a else None, "industry": clean(ind.get_text(" ", strip=True)) if ind else None,
                      "desc": clean(d.get_text(" ", strip=True)) if d else None})
    out, used = [], set()
    for p in posts:
        name = html_text(p["title"]["rendered"])
        if not name:
            continue
        n = norm(name)
        match = None
        for k, c in enumerate(cards):
            if k in used:
                continue
            dom = norm(urlparse(c["url"] or "").netloc.replace("www.", "").split(".")[0])
            if (c["desc"] and norm(c["desc"][:len(name) + 3]).startswith(n)) or (dom and (dom == n or dom == p["slug"].replace("-", "") or ALIASES.get(name.lower()) == dom)):
                match = k; break
        c = cards[match] if match is not None else {}
        if match is not None:
            used.add(match)
        secs = [inds[i] for i in p.get("industries") or [] if i in inds]
        for x in (c.get("industry") or "").split(","):
            if x.strip() and x.strip() not in secs:
                secs.append(x.strip())
        out.append(rec(name, c.get("desc"), c.get("url"), PRIMARY, SOURCE_URL, scraped_at, sectors=secs,
                       sector_map={"cyber": ["Cybersecurity"], "medical devices": ["Health"], "fintech": ["FinTech / Insurance"],
                                   "insurtech": ["FinTech / Insurance"], "digital health": ["Health"], "deep tech": ["Deeptech / Robotics / AR/VR"],
                                   "robotics": ["Deeptech / Robotics / AR/VR"], "industry 4.0": ["Deeptech / Robotics / AR/VR"],
                                   "space": ["Deeptech / Robotics / AR/VR"], "enterprise saas": ["Dev Tools / Cloud"]},
                       on_portfolio_page=match is not None))
    finish(out, "tend", ("description", "company_url", "everywhere_tags"))
    print("cards unmatched:", [c["url"] for k, c in enumerate(cards) if k not in used])


if __name__ == "__main__":
    main()
