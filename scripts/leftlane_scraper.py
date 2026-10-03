#!/usr/bin/env python3
"""Left Lane Capital portfolio scraper -> leftlane_companies.json
Source: https://www.leftlane.com/companies — Webflow showcase blocks.
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

SOURCE_URL = "https://www.leftlane.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "leftlane_companies.json")
PRIMARY = "Left Lane Capital"

NAME_RE = re.compile(
    r"^([A-Z0-9][\w\'\.\-&]*(?:\s+[A-Z0-9][\w\'\.\-&]*){0,4})\s+"
    r"(?:is|are|helps|provides|offers|enables|lets|turns|democratizing|acquires|"
    r"builds|building|creates|operates|delivers|connects|powers|makes|brings|"
    r"transforms|reimagines|designs|develops|runs|owns|manages)",
    re.I,
)


def name_from_desc_or_url(desc, href):
    if desc:
        m = NAME_RE.match(desc.strip())
        if m:
            return clean(m.group(1))
    if href:
        host = urlparse(href).netloc.lower().replace("www.", "")
        base = host.split(".")[0] if host else None
        if base and base not in ("bit", "get", "try", "use", "app", "go"):
            return clean(base.replace("-", " ").title())
    return None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for block in soup.select(".showcase-block"):
        desc_el = block.select_one(".showcase-description-copy, p.body-xs, p")
        desc = clean(desc_el.get_text()) if desc_el else None
        website = None
        for a in block.select("a[href^='http']"):
            href = a["href"]
            if "leftlane" in href or "webflow" in href or "website-files" in href:
                continue
            website = clean(href)
            break
        # location + tags from filter fields in parent
        parent = block.find_parent()
        location = None
        sectors = []
        scope = parent if parent else block
        for el in scope.select('[fs-cmsfilter-field="location"]'):
            t = clean(el.get_text())
            if t and t.lower() != "all" and not el.find_parent(class_=re.compile("hide")):
                # prefer visible non-All
                if "hide" not in (el.get("class") or []) and t.lower() != "all":
                    location = t
        # industries in nested dyn items
        for el in scope.select('.industry [fs-cmsfilter-field="tag"], [fs-cmsfilter-field="tag"]'):
            t = clean(el.get_text())
            if t and t.lower() != "all" and t not in sectors:
                if "hide" in " ".join(el.get("class") or []):
                    continue
                # skip filter radio labels at page top
                if el.find_parent("label"):
                    continue
                sectors.append(t)
        name = name_from_desc_or_url(desc, website)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        # strip trailing location/All noise from description if embedded
        if desc:
            desc = re.sub(r"\s+(North America|Europe|Asia|India|Africa|South America|Australia|All)\s+(All\s+)*.*$", "", desc).strip()
            desc = clean(desc)
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": "Active",
            "stage": None,
            "location": location,
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
    print(f"  location: {sum(1 for r in out if r.get('location'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
