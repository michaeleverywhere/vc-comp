#!/usr/bin/env python3
"""Konvoy Ventures portfolio scraper -> konvoy_companies.json
Source: https://www.konvoy.vc/portfolio — Webflow dyn items linking to /portfolio/{slug}.
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.konvoy.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "konvoy_companies.json")
PRIMARY = "Konvoy"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    for a in soup.select('a[href^="/portfolio/"]'):
        href = a.get("href") or ""
        if href.rstrip("/") == "/portfolio":
            continue
        parent = a.find_parent(class_=re.compile(r"w-dyn-item"))
        scope = parent if parent else a
        raw = clean(scope.get_text(" ", strip=True)) or ""
        # Pattern: sectors... Invested: DATE Location: LOC description Name/Stealth
        invested = None
        location = None
        m = re.search(r"Invested:\s*([A-Za-z]+\s+\d{4})", raw)
        if m:
            invested = clean(m.group(1))
        m = re.search(r"Location:\s*(.+?)(?:\s{2,}|Long |High-|Aerospace|Stealth|$)", raw)
        # Better parse: split on Invested/Location
        parts = re.split(r"Invested:\s*", raw, maxsplit=1)
        sectors = []
        desc = None
        name = None
        if len(parts) == 2:
            before = parts[0].strip()
            # before may be sector tags
            for tok in re.split(r"\s{2,}|\s+(?=[A-Z][a-z]+(?:\s+[A-Z])*)", before):
                pass
            # sectors often like "Critical Industries Deep Tech & Hardware"
            sectors_raw = before
            after = parts[1]
            loc_m = re.search(r"Location:\s*(.+)", after)
            if loc_m:
                rest = loc_m.group(1).strip()
                # location until description — location often City, ST or "To be announced"
                loc_m2 = re.match(
                    r"(To be announced|[A-Za-z .]+(?:,\s*[A-Z]{2})?)\s+(.+)$",
                    rest,
                )
                if loc_m2:
                    location = clean(loc_m2.group(1))
                    tail = loc_m2.group(2).strip()
                else:
                    location = clean(rest)
                    tail = ""
            else:
                tail = after
            # tail ends with company name (last word/phrase) — often "Stealth" or brand
            # Description is everything before the final name token(s)
            # Card text example: "Long range modular glider systems Stealth"
            if tail:
                # If ends with Stealth, name=Stealth + slug disambiguation
                if tail.endswith(" Stealth") or tail == "Stealth":
                    name = "Stealth"
                    desc = clean(re.sub(r"\s*Stealth$", "", tail)) or None
                else:
                    # last 1-3 capitalized tokens as name if short; else whole as desc and slug as name
                    tokens = tail.split()
                    if len(tokens) >= 2 and tokens[-1][0].isupper() and len(tokens[-1]) <= 30:
                        # heuristic: last word is name when previous looks like sentence
                        name = tokens[-1]
                        desc = clean(" ".join(tokens[:-1])) or None
                    else:
                        desc = clean(tail)
                        name = None
            if sectors_raw:
                # split known multi-word sector labels present on Konvoy
                for label in [
                    "Critical Industries", "Deep Tech & Hardware", "Developer Tools & Infrastructure",
                    "Gaming", "Media & Entertainment", "Web3", "Consumer", "Enterprise",
                    "Fintech", "Health", "Climate",
                ]:
                    if label.lower() in sectors_raw.lower():
                        sectors.append(label)
        # Fallback name from slug
        slug = href.rstrip("/").split("/")[-1]
        if not name:
            if slug.startswith("stealth"):
                name = f"Stealth ({slug})"
            else:
                name = clean(slug.replace("-", " ").title())
        elif name.lower() == "stealth":
            name = f"Stealth ({slug})"

        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())

        # first_invested is a date on site, not a funding round — leave stage blank
        profile = urljoin(SOURCE_URL, href)
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": None,
            "status": "Active",
            "stage": None,
            "location": location if location and location.lower() != "to be announced" else None,
            "sectors": sectors or None,
            "invested_date": invested,
            "everywhere_tags": classify(name, desc, sectors)[:4],
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
    print(f"  location: {sum(1 for r in out if r.get('location'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
