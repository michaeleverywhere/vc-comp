#!/usr/bin/env python3
"""Ada Ventures portfolio scraper -> ada_companies.json
Source: homepage Webflow company-collection-wrapper cards -> /company/{slug}
detail pages for name, website, stage, theme.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, stage_label, fetch_many, is_social
from _d20_common import write_out

SOURCE_URL = "https://www.adaventures.com/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "ada_companies.json")
PRIMARY = "Ada Ventures"
SECTOR_MAP = {
    "climate equity": ["Climate / Sustainability"],
    "economic empowerment": ["FinTech / Insurance", "Future of Work"],
    "healthy ageing": ["Health", "BioTech"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    wrap = soup.select_one(".company-collection-wrapper")
    items = wrap.select(".w-dyn-item") if wrap else []
    cards = []
    for it in items:
        a = it.find("a", href=True)
        if not a:
            continue
        href = a["href"]
        if "/company/" not in href:
            continue
        detail = urljoin(SOURCE_URL, href)
        text = clean(it.get_text(" "))
        theme = stage_raw = fund = None
        # text like "Climate Equity Fund II Pre-seed"
        for theme_name in ("Climate Equity", "Economic Empowerment", "Healthy Ageing"):
            if text and theme_name.lower() in text.lower():
                theme = theme_name
                break
        for s in ("Pre-seed", "Pre-Seed", "Seed", "Series A"):
            if text and re.search(rf"\b{re.escape(s)}\b", text, re.I):
                stage_raw = s
                break
        slug = href.rstrip("/").split("/")[-1]
        cards.append((slug, detail, theme, stage_raw))

    pages = fetch_many([d for _, d, _, _ in cards], workers=6, pause=0.12)
    out, seen = [], set()
    for slug, detail, theme, stage_raw in cards:
        html = pages.get(detail) or ""
        ds = BeautifulSoup(html, "html.parser") if html else None
        name = slug.replace("-", " ").title()
        website = desc = None
        stage = stage_label(stage_raw) if stage_raw else None
        if ds:
            for h in ds.find_all("h1"):
                t = clean(h.get_text(" "))
                if t and t.lower() not in ("back to portfolio", "website", "ceo", "team", "portfolio", "faq") and len(t) < 60:
                    name = t
                    break
            for a in ds.select("a[href^=http]"):
                href = a["href"]
                label = (clean(a.get_text(" ")) or "").lower()
                if "adaventures" in href or is_social(href):
                    continue
                if label in ("website",) or (label and "." in label and len(label) < 40):
                    website = clean_url(href if href.startswith("http") else f"https://{label}")
                    if label == "website" or website:
                        if label == "website" or (label and "." in label):
                            website = clean_url(href)
                            break
            # stage from detail if present
            for h in ds.find_all(["h1", "h2", "p", "div"]):
                t = clean(h.get_text(" "))
                if t and t.lower() == "initial investment stage":
                    nxt = h.find_next(["h1", "h2", "p", "div"])
                    if nxt:
                        stage = stage_label(clean(nxt.get_text(" "))) or stage
                    break
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        sectors = [theme] if theme else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": sectors,
            "stage": stage,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("company_url", "sectors", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
