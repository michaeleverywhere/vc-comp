#!/usr/bin/env python3
"""G Squared portfolio scraper -> gsquared_companies.json
Source: https://www.gsquared.com/portfolio/ — SSR article cards + detail pages
for description/website. EXITED badge visible in section headers / card context.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, fetch_many
from _d20_common import write_out

SOURCE_URL = "https://www.gsquared.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "gsquared_companies.json")
PRIMARY = "G Squared"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = []
    for art in soup.select("article.portfolio-grid__slide, article"):
        a = art.select_one("a[href*='/portfolio/']")
        h = art.select_one("h3, h2")
        if not a or not h:
            continue
        name = clean(h.get_text(" "))
        href = a["href"]
        if not name:
            continue
        cards.append((name, href))
    # also parse EXITED context from nearby text on list page
    list_html = str(soup)
    pages = fetch_many([h for _, h in cards], workers=6, pause=0.15)
    out, seen = [], set()
    for name, href in cards:
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        html = pages.get(href) or ""
        dsoup = BeautifulSoup(html, "html.parser") if html else None
        desc = website = None
        status = None
        if dsoup:
            for el in dsoup.select(".entry-content p, article p, .portfolio-single p"):
                t = clean(el.get_text(" "))
                if t and len(t) > 40:
                    desc = t
                    break
            for a in dsoup.find_all("a", href=True):
                h = a["href"]
                label = (clean(a.get_text(" ")) or "").lower()
                if h.startswith("http") and "gsquared.com" not in h and label in ("website", "visit website", "company website", "visit"):
                    website = clean_url(h)
                    break
            if re.search(r"(?i)\bexited\b|\bacquired\b", dsoup.get_text(" ")):
                # only if clearly about this company exit on the page title area
                title = clean(dsoup.title.get_text(" ")) if dsoup.title else ""
                if re.search(r"(?i)exit|acquir", title or ""):
                    status = "acquired"
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "sectors": [],
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
