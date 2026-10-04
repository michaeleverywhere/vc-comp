#!/usr/bin/env python3
"""Brighteye Ventures portfolio scraper -> brighteye_companies.json
Source: https://www.brighteyevc.com/portfolio — Webflow CMS collection.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.brighteyevc.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "brighteye_companies.json")
PRIMARY = "Brighteye Ventures"


def slug_to_name(slug: str) -> str:
    slug = slug.strip("/").split("/")[-1]
    slug = re.sub(r"-copy$", "", slug)
    parts = slug.replace("-", " ").split()
    return " ".join(p.capitalize() if p.lower() not in ("the", "and", "of", "for") else p.lower() for p in parts).strip()


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    # Featured cards: rich description + website
    featured = {}
    for it in soup.select(".featured-companies-collection-item.w-dyn-item"):
        h = it.select_one("h4, h3, h2")
        name = clean(h.get_text()) if h else None
        if not name:
            continue
        short = None
        el = it.select_one(".featured-portfolio-description")
        if el:
            short = clean(el.get_text())
        about = None
        texts = [clean(t) for t in it.stripped_strings if clean(t)]
        for i, t in enumerate(texts):
            if t == "About" and i + 1 < len(texts) and len(texts[i + 1]) > 40:
                about = texts[i + 1]
                break
        website = None
        for a in it.select("a[href^='http']"):
            href = a["href"]
            if any(x in href for x in ["brighteye", "webflow", "linkedin", "twitter"]):
                continue
            website = clean(href)
            break
        loc = None
        for chip in it.select(".dark-chip .sub-head-small"):
            ct = clean(chip.get_text())
            if ct and ct not in ("Work", "Learning", "more", "About") and "/" in ct or (ct and len(ct) <= 30 and ct[0].isupper()):
                if ct not in ("Work", "Learning", "Exited"):
                    loc = ct
        featured[name.lower()] = {
            "name": name,
            "description": about or short,
            "company_url": website,
            "location": loc,
        }

    for it in soup.select(".portfolio-companies-collection-list .w-dyn-item"):
        a = it.select_one("a[href*='/portfolio-companies/']")
        href = a.get("href") if a else None
        if not href:
            continue
        name = slug_to_name(href)
        # Prefer prettier name from featured if same slug family
        for fname, info in featured.items():
            if fname.replace(" ", "-") in href.replace("_", "-").lower() or info["name"].lower().replace(" ", "-") in href.lower():
                name = info["name"]
                break
        if name.lower() in seen:
            continue
        seen.add(name.lower())

        location = None
        for chip in it.select(".dark-chip.is-outline .sub-head-small"):
            ct = clean(chip.get_text())
            if ct:
                location = ct
                break
        status = "active"
        exit_tag = it.select_one(".exit-tag:not(.w-condition-invisible)")
        if exit_tag and clean(exit_tag.get_text()):
            status = "acquired"
        # also check invisible class absence
        for tag in it.select(".exit-tag"):
            classes = " ".join(tag.get("class") or [])
            if "w-condition-invisible" not in classes:
                txt = clean(tag.get_text())
                if txt and "exit" in txt.lower():
                    status = "acquired"

        info = featured.get(name.lower()) or {}
        desc = info.get("description")
        website = info.get("company_url")
        if not location:
            location = info.get("location")

        # sector chips (Work / Learning etc.) — use as light sector signal
        sectors = []
        for chip in it.select(".dark-chip .sub-head-small"):
            ct = clean(chip.get_text())
            if ct in ("Work", "Learning") and ct not in sectors:
                sectors.append(ct)

        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": None,
            "location": location,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, desc, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": urljoin(SOURCE_URL, href),
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    # Add any featured not in list
    for key, info in featured.items():
        if key in seen:
            continue
        seen.add(key)
        rec = {
            "company_name": info["name"],
            "description": info.get("description"),
            "company_url": info.get("company_url"),
            "status": "active",
            "stage": None,
            "location": info.get("location"),
            "sectors": None,
            "everywhere_tags": classify(info["name"], info.get("description"))[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  location: {sum(1 for r in out if r.get('location'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
