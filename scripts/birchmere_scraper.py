#!/usr/bin/env python3
"""Birchmere Ventures portfolio scraper -> birchmere_companies.json
Source: https://birchmerevc.com/portfolio/ — Visual Portfolio grid (every ?vp_page=N page): each tile gives the
company name with its city/state and Birchmere's categories; each company page adds the description and website."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, fetch, fetch_many, label_after, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://birchmerevc.com/portfolio/"
PRIMARY = "Birchmere Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    items = {}
    for p in range(1, 15):
        html = fetch(SOURCE_URL if p == 1 else f"{SOURCE_URL}?vp_page={p}")
        s = BeautifulSoup(html, "html.parser")
        new = 0
        for it in s.select("article.vp-portfolio__item-wrap"):
            a = it.select_one("a[aria-label][href]")
            if not a or a["href"] in items:
                continue
            cats = [clean(x.get_text(" ", strip=True)) for x in it.select(".vp-portfolio__item-meta-category")]
            items[a["href"]] = (clean(a["aria-label"]), [c for c in cats if c])
            new += 1
        if not new:
            break
    pages = fetch_many(list(items), workers=4, pause=0.3)
    out = []
    for u, (label, cats) in items.items():
        m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", label)
        name, loc = (clean(m.group(1)), clean(m.group(2))) if m else (label, None)
        desc = web = None
        h = pages.get(u)
        if h:
            d = BeautifulSoup(h, "html.parser")
            for t in d(["script", "style", "nav", "footer", "header"]):
                t.decompose()
            strs = [x for x in (clean(z) for z in d.stripped_strings) if x]
            name = label_after(strs, "Client") or name
            cat2 = label_after(strs, "Category")
            if cat2 and not cat2.endswith(":") and not cats:
                cats = [c.strip() for c in cat2.split(",") if c.strip()]
            if label in strs:
                i = strs.index(label)
                if i + 1 < len(strs) and strs[i + 1].rstrip(":") not in ("Client", "Category") and len(strs[i + 1]) > 30:
                    desc = strs[i + 1]
            for a in d.select("a[href^=http]"):
                href = a["href"].strip()
                if "birchmerevc.com" not in href and not is_social(href) and "wordpress" not in href:
                    web = href
                    break
        st = "acquired" if desc and re.search(r"\b(acquired by|was acquired|IPO'?ed|went public)\b", desc, re.I) else None
        out.append(rec(name, desc, web, PRIMARY, SOURCE_URL, scraped_at, sectors=cats, location=loc, profile_url=u, status=st))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} Birchmere companies")
    finish(out, "birchmere", ("description", "company_url", "sectors", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
