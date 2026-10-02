#!/usr/bin/env python3
"""Lunar Ventures portfolio scraper -> lunarventures_companies.json
Source: https://lunar.vc/portfolio — static HTML investment cards.
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlparse

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://lunar.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "lunarventures_companies.json")
PRIMARY = "Lunar Ventures"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    cards = soup.select(".card") or []
    for card in cards:
        text = card.get_text("\n", strip=True)
        lines = [clean(l) for l in text.split("\n") if clean(l)]
        # filter chips / noise
        lines = [l for l in lines if l and l not in ("@", "All", "Infra", "Applications", "Tech-Bio", "Autonomy")]
        if not lines:
            continue
        status = "Active"
        acquirer = None
        # "Acquired by X" often precedes the @ name block
        for l in list(lines):
            m = re.match(r"^Acquired by\s+(.+)$", l, re.I)
            if m:
                status = "Exited"
                acquirer = clean(m.group(1))
                lines.remove(l)
        website = None
        for a in card.select("a[href^='http']"):
            href = a["href"]
            if "lunar.vc" not in href:
                website = clean(href)
                break
        # Also bare URLs as text
        if not website:
            for l in lines:
                if re.match(r"^https?://", l) or (l.startswith("www.") and "." in l):
                    website = l if l.startswith("http") else "https://" + l
                    break
        # name: first non-URL, non-acquired line
        name = None
        desc = None
        for l in lines:
            if re.match(r"^https?://", l) or l.startswith("www."):
                continue
            if l.startswith("Acquired"):
                continue
            if not name:
                name = l
            elif not desc:
                desc = l
        if not name or name.lower() in seen:
            continue
        if len(name) > 80:
            continue
        seen.add(name.lower())
        # Infer sector chips from page filters if present on card classes/data
        sectors = []
        card_cls = " ".join(card.get("class") or []).lower()
        for label, key in [("Infra", "infra"), ("Applications", "application"), ("Tech-Bio", "tech-bio"), ("Autonomy", "autonomy")]:
            if key in card_cls:
                sectors.append(label)
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "acquirer": acquirer,
            "stage": None,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, desc, sectors)[:4],
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
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")


if __name__ == "__main__":
    main()
