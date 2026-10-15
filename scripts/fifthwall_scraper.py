#!/usr/bin/env python3
"""Fifth Wall portfolio scraper -> fifthwall_companies.json
Source: https://fifthwall.com/portfolio — Webflow CMS items with company name
in h2, description prose, and exit/IPO notes encoded in the name suffix.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://fifthwall.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "fifthwall_companies.json")
PRIMARY = "Fifth Wall"
TAG_OVERRIDES = {}


def parse_name(raw):
    status = acquirer = ticker = None
    name = raw
    if re.search(r"(?i)exited|acquired|nyse|nasdaq", raw):
        if re.search(r"(?i)acquired by\s+([^—(]+)", raw):
            m = re.search(r"(?i)acquired by\s+([^—(]+)", raw)
            status = "acquired"
            acquirer = clean(m.group(1))
        elif re.search(r"(?i)exited", raw):
            status = "acquired"
        if re.search(r"(?i)\((?:NYSE|NASDAQ):\s*([A-Z.]+)\)", raw):
            m = re.search(r"(?i)\((?:NYSE|NASDAQ):\s*([A-Z.]+)\)", raw)
            ticker = m.group(1).upper()
            status = status or "public"
        name = re.split(r"\s*[—–-]\s*(?:Exited|Acquired)", raw, maxsplit=1)[0]
        name = re.sub(r"\s*\((?:NYSE|NASDAQ):\s*[A-Z.]+\)\s*", "", name).strip()
    return clean(name), status, acquirer, ticker


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".w-dyn-item"):
        h = it.select_one("h2")
        if not h:
            continue
        raw = clean(h.get_text(" "))
        if not raw or raw in ("Featured", "Exited", "ALL") or raw.lower().startswith("got questions"):
            continue
        name, status, acquirer, ticker = parse_name(raw)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        # description: look for medium text blocks
        desc = None
        for el in it.select("p, div"):
            t = clean(el.get_text(" "))
            if t and len(t) > 60 and name.split()[0].lower() in t.lower()[:80]:
                # strip leading name repeats
                desc = t
                break
        if not desc:
            texts = [clean(t) for t in it.stripped_strings]
            texts = [t for t in texts if t and t != raw and len(t) > 60]
            if texts:
                desc = texts[0]
        website = None
        for a in it.select("a[href]"):
            href = a.get("href") or ""
            if href.startswith("http") and "fifthwall.com" not in href and not any(x in href for x in ("linkedin", "twitter", "facebook")):
                website = clean_url(href)
                break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "acquirer": acquirer,
            "ticker_symbol": ticker,
            "sectors": [],
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
