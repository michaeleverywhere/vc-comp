#!/usr/bin/env python3
"""NextView Ventures portfolio scraper -> nextviewventures_companies.json
Source: https://nextview.vc/investments/all/ — NextView Ventures, seed-stage venture firm (NYC/Boston/SF). Every
company on the "All" tab has a modal block (id = company slug) with founded year, invested year, description,
location, investment area, website link and an Acquired flag on its tile. The site renders company names only as logo
images, so the name is taken from the site's own modal text: the leading words of the description (or another
capitalised phrase in the modal) whose letters match the company slug. Companies whose name can't be confirmed that
way are skipped rather than guessed."""
import os, sys, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url
from _d50_common import rec, finish

SOURCE_URL = "https://nextview.vc/investments/all/"
PRIMARY = "NextView Ventures"


def norm(x):
    return re.sub(r"[^a-z0-9]", "", x.lower())


def name_from(slug, texts):
    toks = slug.split("-")
    prefixes = {norm("".join(toks[:n])) for n in range(1, len(toks) + 1)}
    for text in texts:
        words = text.split()
        starts = range(len(words))
        for st in starts:
            best = None
            for k in range(1, 9):
                if st + k > len(words):
                    break
                cand = re.sub(r"[®™“”\"(]", "", " ".join(words[st:st + k]))
                cand = re.sub(r"(’s|'s)$", "", cand).rstrip(",.:;)")
                if cand and cand[0].isupper() and norm(cand) in prefixes:
                    best = cand
            if best:
                return best
    return None


def info(m, label):
    for d in m.select(".info"):
        t = d.select_one(".info-title")
        if t and clean(t.get_text(" ")).rstrip(": ").startswith(label):
            v = d.select_one(".info-data")
            if v is None:  # Investment Area value sits inside the title div after a comment
                return clean(t.get_text(" ").split(":", 1)[-1])
            return clean(v.get_text(" "))
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    acquired = set()
    for tile in soup.select("[data-page-target]"):
        if tile.select_one(".exited"):
            acquired.add(tile["data-page-target"])
    out, skipped = [], []
    for m in soup.select("div.modal-page.investments-modal-content"):
        slug = m.get("id")
        p = m.select_one("h3.excerpt p")
        desc = clean(p.get_text(" ")) if p else None
        bottom = m.select_one(".bottom-text")
        name = name_from(slug, [desc or "", clean(bottom.get_text(" ")) if bottom else ""])
        if not name:
            skipped.append(slug)
            continue
        if desc and norm(name) not in norm(desc):
            desc = None  # description doesn't mention this company (site mix-up); don't attach it
        a = m.find("a", string=re.compile("Visit Website"))
        area = info(m, "Investment Area")
        out.append(rec(name, desc, clean_url(a["href"]) if a and a.get("href") else None, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=[s.strip() for s in (area or "").split(",") if s.strip()],
                       founded=info(m, "Founded"), year_invested=info(m, "Invested"), location=info(m, "Location"),
                       status="Acquired" if slug in acquired else None))
    print(f"skipped (name not confirmable from site text): {skipped}")
    if len(out) < 100:
        raise SystemExit(f"FATAL: only {len(out)} NextView companies")
    finish(out, "nextviewventures", ("description", "company_url", "founded", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
