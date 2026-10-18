#!/usr/bin/env python3
"""Distributed Ventures portfolio scraper -> distributedventures_companies.json
Source: https://www.distributedvc.com/portfolio — Webflow CMS cards: description,
website, fund ("Distributed Ventures" vs "Prior Investments") and the Acquired badge
(only when not hidden); each card's /portfolio/<slug> page lists its categories.
Card names are not published as text, so the name is taken from the description's
leading words when they match the slug, else the slug title-cased."""
import os, re, sys, time
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.distributedvc.com/portfolio"
PRIMARY = "Distributed Ventures"
SECTOR_MAP = {"wealth": ["FinTech / Insurance"], "insurance": ["FinTech / Insurance"], "health": ["Health"],
              "fintech": ["FinTech / Insurance"], "climate": ["Climate / Sustainability"]}


def squash(x):
    return re.sub(r"[^a-z0-9]", "", (x or "").lower())


def name_for(slug, desc):
    target = squash(slug)
    words = (desc or "").split()
    for k in range(1, 6):
        cand = " ".join(words[:k]).rstrip(",.:;")
        if squash(cand) == target or squash(re.sub(r"(?i)^the\s+", "", cand)) == target:
            return cand
    if desc and "-" not in slug and desc[:len(slug)].lower() == slug.lower():
        return desc[:len(slug)]
    m = re.match(r"([A-Z][\w.&'()-]*(?:\s+[A-Z][\w.&'()-]*){0,3})\s+(is|helps|was|automates|provides|makes|offers|simplifies)\b", desc or "")
    if m and squash(m.group(1)).startswith(target[:4]):
        return m.group(1)
    return " ".join(w.capitalize() for w in slug.split("-"))


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in s.select(".portfolio-item.extended.w-dyn-item"):
        a = it.select_one("a.portfolio-link-hide[href]")
        if not a:
            continue
        slug = a["href"].rstrip("/").split("/")[-1]
        dp = it.select_one(".portfolio-paragraph .w-richtext")
        desc = clean(dp.get_text(" ", strip=True)) if dp else None
        w = it.select_one("a.port-link-over[href^=http]")
        fund = it.select_one('[fs-cmsfilter-field="fund"]')
        fund = clean(fund.get_text(" ", strip=True)) if fund else None
        acq = it.select_one(".acquired-div")
        acquired = acq is not None and "w-condition-invisible" not in (acq.get("class") or [])
        cats = []
        try:
            d = BeautifulSoup(fetch(urljoin(SOURCE_URL, a["href"])), "html.parser")
            for t in d(["script", "style", "svg", "nav"]):
                t.decompose()
            cats = [c for c in (clean(x) for x in d.stripped_strings) if c and c != "Distributed Ventures"]
        except Exception as e:
            print("  detail failed", slug, e)
        time.sleep(0.2)
        out.append(rec(name_for(slug, desc), desc, w["href"] if w and not is_social(w["href"]) else None, PRIMARY,
                       SOURCE_URL, scraped_at, sectors=cats, sector_map=SECTOR_MAP,
                       fund=fund, status="acquired" if acquired else "active",
                       profile_url=urljoin(SOURCE_URL, a["href"])))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Distributed Ventures companies")
    finish(out, "distributedventures", ("description", "company_url", "fund", "status", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
