#!/usr/bin/env python3
"""Contour Venture Partners portfolio scraper -> contour_companies.json
Source: https://contourventures.com/portfolio/ — Elementor portfolio popups
with website + description; exited companies live in portfolio-box-exited columns.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://contourventures.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "contour_companies.json")
PRIMARY = "Contour Venture Partners"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for box in soup.select("[class*='portfolio-box']"):
        pop = box.select_one(".portfolio-popup")
        if not pop:
            continue
        # name from id or img filename
        pid = pop.get("id") or ""
        img = pop.select_one("img")
        name = None
        if img and img.get("src"):
            base = img["src"].split("/")[-1]
            base = re.sub(r"\.(png|jpg|jpeg|webp|svg)$", "", base, flags=re.I)
            name = clean(base.replace("-", " ").replace("_", " ").title())
        # better: first link text / alt
        a = pop.select_one("a[href]")
        website = clean_url(a["href"]) if a and a.get("href", "").startswith("http") else None
        p = pop.select_one("p")
        desc = clean(p.get_text(" ")) if p else None
        # try to pull a display name from description start or id
        if pid:
            name = clean(pid.replace("-", " ").title()) or name
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        status = None
        acquirer = None
        if desc and re.search(r"(?i)acquired by", desc):
            status = "acquired"
            m = re.search(r"(?i)acquired by\s+([^.]+)", desc)
            if m:
                acquirer = clean(m.group(1))
        if "portfolio-box-exited" in " ".join(box.get("class", [])):
            status = status or "acquired"
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "acquirer": acquirer,
            "sectors": [],
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
