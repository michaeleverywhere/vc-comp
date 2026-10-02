#!/usr/bin/env python3
"""BoxGroup portfolio scraper -> boxgroup_companies.json
Source: https://boxgroup.com/category/{enterprise,consumer,fintech,healthcare,exits}
Site publishes logo+URL cards (no text names); names derived from domain labels.
"""
import json, os, re, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from urllib.parse import urlparse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

CATEGORIES = {
    "enterprise": "https://boxgroup.com/category/enterprise",
    "consumer": "https://boxgroup.com/category/consumer",
    "fintech": "https://boxgroup.com/category/fintech",
    "healthcare": "https://boxgroup.com/category/healthcare",
    "exits": "https://boxgroup.com/category/exits",
}
SOURCE_URL = "https://boxgroup.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "boxgroup_companies.json")
PRIMARY = "BoxGroup"

# Well-known domain -> display name overrides (site shows logos only)
DOMAIN_NAMES = {
    "clay.run": "Clay",
    "tryramp.com": "Ramp",
    "baseten.co": "Baseten",
    "cursor.sh": "Cursor",
    "plaid.com": "Plaid",
    "airtable.com": "Airtable",
    "amplitude.com": "Amplitude",
    "scopely.com": "Scopely",
    "stripe.com": "Stripe",
    "warp.dev": "Warp",
    "flyzipline.com": "Zipline",
    "warbyparker.com": "Warby Parker",
    "flatiron.com": "Flatiron Health",
    "pillpack.com": "Pillpack",
    "harrys.com": "Harry's",
    "casetext.com": "Casetext",
    "mavenclinic.com": "Maven Clinic",
    "thebrowser.company": "The Browser Company",
    "a.team": "A.Team",
    "id.me": "ID.me",
    "ro.co": "Ro",
    "getmoss.com": "Moss",
    "nothing.tech": "Nothing",
    "meta.com": "Meta",
}


def domain_of(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


_SKIP_LABELS = {
    "www", "www2", "m", "mobile", "app", "apps", "en", "us", "uk", "eu", "de", "fr",
    "es", "jp", "br", "ca", "au", "in", "co", "about", "blog", "news", "help",
    "support", "docs", "developer", "developers", "api", "cdn", "static",
}


def registrable_host(host: str) -> str:
    parts = host.split(".")
    if len(parts) >= 3 and parts[0] in _SKIP_LABELS:
        return ".".join(parts[1:])
    return host


def name_from_domain(host: str) -> str:
    host = registrable_host(host)
    if host in DOMAIN_NAMES:
        return DOMAIN_NAMES[host]
    # Keep short brand TLDs readable: id.me -> ID.me, ro.co -> Ro
    parts = host.split(".")
    label = parts[0].replace("-", " ").replace("_", " ")
    if host in ("id.me",):
        return "ID.me"
    if host in ("ro.co",):
        return "Ro"
    if host in ("a.team",):
        return "A.Team"
    if host.startswith("get") and len(label) > 3:
        # getmoss.com -> Moss is wrong; keep Getmoss / Moss from DOMAIN_NAMES if needed
        pass
    return label.title() if label else host


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    by_url = {}  # url -> {name, sectors, status}
    for cat, url in CATEGORIES.items():
        html = fetch(url)
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select("a[href^='http']"):
            href = clean(a["href"])
            if not href or "boxgroup.com" in href or "webflow" in href or "facebook" in href:
                continue
            # skip asset/cdn
            if any(x in href for x in ("cdn.prod.website-files", "googleapis", "twitter.com", "linkedin.com")):
                continue
            host = domain_of(href)
            if not host or "." not in host:
                continue
            key = registrable_host(host)
            # Prefer cleaner apex URLs when we only saw a locale subdomain
            entry = by_url.setdefault(key, {
                "company_url": href if href.startswith("http") else "https://" + href,
                "company_name": name_from_domain(host),
                "sectors": set(),
                "status": "Active",
            })
            if cat == "exits":
                entry["status"] = "Exited"
            elif cat != "exits":
                entry["sectors"].add(cat.title())
        # polite
        import time; time.sleep(0.4)

    out, seen = [], set()
    for host, entry in sorted(by_url.items(), key=lambda x: x[1]["company_name"].lower()):
        name = entry["company_name"]
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        sectors = sorted(entry["sectors"])
        rec = {
            "company_name": name,
            "description": None,
            "company_url": entry["company_url"],
            "status": entry["status"],
            "stage": None,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, None, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
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
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")


if __name__ == "__main__":
    main()
