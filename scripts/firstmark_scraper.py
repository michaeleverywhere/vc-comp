#!/usr/bin/env python3
"""FirstMark Capital portfolio scraper -> firstmark_companies.json
Source: https://firstmark.com/portfolio/ — portfolio-shape cards (+ optional detail pages).
"""
import json, os, re, sys, time
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, HEADERS

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://firstmark.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "firstmark_companies.json")
PRIMARY = "FirstMark"

TICKER_RE = re.compile(r"\b((?:NYSE|NASDAQ|LSE|HKEX|NSE):\s*[A-Z0-9.]+)\b", re.I)
ACQUIRED_RE = re.compile(r"^Acquired by\s+(.+)$", re.I)


def website_from_detail(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a[href^='http']"):
            href = a["href"]
            text = (a.get_text() or "").lower()
            if any(x in href for x in ["firstmark", "efrontcloud", "twitter", "linkedin", "x.com", "facebook", "instagram"]):
                continue
            if "visit" in text or True:
                # Prefer "Visit X" links
                if "visit" in text:
                    return clean(href)
        # fallback first external non-social
        for a in soup.select("a[href^='http']"):
            href = a["href"]
            if any(x in href for x in ["firstmark", "efrontcloud", "twitter", "linkedin", "x.com", "facebook", "instagram"]):
                continue
            return clean(href)
        return None
    except Exception:
        return None


def parse_shape(shape):
    heading = shape.select_one(".portfolio-shape__heading")
    text_el = shape.select_one(".portfolio-shape__text")
    ticker_el = shape.select_one(".portfolio-shape__ticker")
    desc = clean(text_el.get_text()) if text_el else None
    ticker = clean(ticker_el.get_text()) if ticker_el else None
    name = clean(heading.get_text()) if heading else None

    strings = [clean(t) for t in shape.stripped_strings if clean(t)]
    # Remove desc/ticker from consideration for name
    extras = []
    for s in strings:
        if desc and s == desc:
            continue
        if ticker and s == ticker:
            continue
        tm = TICKER_RE.search(s or "")
        if tm and not ticker:
            ticker = clean(tm.group(1))
            rest = clean(TICKER_RE.sub("", s))
            if rest:
                extras.append(rest)
            continue
        am = ACQUIRED_RE.match(s or "")
        if am:
            extras.append(s)
            continue
        extras.append(s)

    if not name:
        # Prefer the last non-acquired token as the company name
        candidates = [e for e in extras if not ACQUIRED_RE.match(e or "")]
        if candidates:
            # Often name is the only/short token; if multiple, last is name
            name = candidates[-1] if len(candidates) > 1 else candidates[0]
            # If first tokens look like description already captured, fine
        elif extras:
            name = extras[0]

    exit_detail = None
    status = "Active"
    for e in extras:
        am = ACQUIRED_RE.match(e or "")
        if am:
            status = "Acquired"
            exit_detail = clean(e)
    if ticker:
        status = "Public"

    # Description may be missing on list cards; acquired blurb is exit_detail not desc
    if desc and ACQUIRED_RE.match(desc):
        exit_detail = desc
        desc = None
        status = "Acquired"

    return name, desc, ticker, status, exit_detail


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    fetch_sites = "--no-detail" not in sys.argv
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    for shape in soup.select(".portfolio-shape"):
        a = shape.find_parent("a")
        profile = urljoin(SOURCE_URL, a["href"]) if a and a.get("href") else SOURCE_URL
        if "status=" in profile or "filter=" in profile:
            continue
        name, desc, ticker, status, exit_detail = parse_shape(shape)
        if not name or name.lower() in seen:
            continue
        if name.lower() in ("active - early", "active - growth", "exited - acquired", "exited - ipo"):
            continue
        seen.add(name.lower())
        website = None
        if fetch_sites and "/portfolio/" in profile and not profile.rstrip("/").endswith("portfolio"):
            website = website_from_detail(profile)
            time.sleep(0.12)
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "exit_detail": exit_detail,
            "ticker_symbol": ticker,
            "stage": None,
            "everywhere_tags": classify(name, desc)[:4],
            "primary_investor": PRIMARY,
            "source_url": profile,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
