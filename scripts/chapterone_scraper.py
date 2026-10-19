#!/usr/bin/env python3
"""Chapter One portfolio scraper -> chapterone_companies.json
Source: https://www.chapterone.com/investments — the "Our investments" section
(JS-rendered, read via headless Chrome): company name, Chapter One's category label and
founding year ("Est. YYYY"), plus the "Meet the authors" founder cards (founder name and
"Founder/CEO of X" -> founders; companies named only there, e.g. Mirage, are added too).
The site publishes no full portfolio list, only these featured companies."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.chapterone.com/investments"
PRIMARY = "Chapter One"
SECTOR_MAP = {"defense tech": ["Deeptech / Robotics / AR/VR"], "fintech": ["FinTech / Insurance"], "dev tools": ["Dev Tools / Cloud"],
              "ai cloud": ["Dev Tools / Cloud"], "banking": ["FinTech / Insurance"], "crypto infra": ["Web3 / Crypto"],
              "staking": ["Web3 / Crypto"], "defi": ["Web3 / Crypto"], "ai research": [], "productivity": ["Future of Work"]}


def spans(sec, cls):
    box = sec.select_one(cls)
    return [clean(x.get_text(" ", strip=True)) for x in box.find_all("span")] if box else []


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 20000, min_len=50000), "html.parser")
    sec = s.select_one("section.inv")
    if not sec:
        raise SystemExit("FATAL: investments section not found")
    names = [clean(x.get_text(" ", strip=True)) for x in sec.select(".inv__list .inv__name")]
    cats, ests = spans(sec, ".inv__category"), spans(sec, ".inv__est")
    founders = {}
    for fc in s.select("figcaption"):
        h3, p = fc.find("h3"), fc.select_one("a.founders__link p")
        if not h3 or not p:
            continue
        m = re.match(r"^(?:Co-?founder|Founder|CEO)(?: and CEO)? of (.+?)(?:\s*\(.*\))?$", clean(p.get_text(" ", strip=True)), re.I)
        if m:
            founders.setdefault(clean(m.group(1)).lower(), []).append(clean(h3.get_text(" ", strip=True)))
    out, seen = [], set()
    for i, n in enumerate(names):
        if not n:
            continue
        cat = cats[i] if i < len(cats) and len(cats) == len(names) else None
        est = ests[i] if i < len(ests) and len(ests) == len(names) else None
        y = re.search(r"(19|20)\d{2}", est or "")
        out.append(rec(n, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [], sector_map=SECTOR_MAP,
                       founded_year=int(y.group(0)) if y else None, founders=founders.get(n.lower()) or None))
        seen.add(n.lower())
    for k, v in founders.items():
        if k not in seen:
            nm = next((x for x in [k.title()]), k)
            out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, founders=v))
    if len(out) < 8:
        raise SystemExit(f"FATAL: only {len(out)} Chapter One companies")
    finish(out, "chapterone", ("sectors", "founded_year", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
