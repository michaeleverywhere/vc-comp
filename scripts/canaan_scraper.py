#!/usr/bin/env python3
"""
Canaan Partners portfolio scraper -> canaan_companies.json

SUBSTITUTE for Atomico (atomico.com returns HTTP 429 from this host after
exhaustive recon — homepage, /portfolio, /companies, sitemap, and r.jina.ai
relay all blocked). Canaan publishes a full public portfolio.

Source: https://www.canaan.com/companies listing (345 `.list-item` cards with
name + current/acquired status) + per-company modal
`GET /company/<slug>/modal` (XHR) returning description, website, investor,
and investment stage.

usage:
    python3 scripts/canaan_scraper.py [--limit N] [--skip-details]
"""
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from html import unescape

import requests
from bs4 import BeautifulSoup

LIST_URL = "https://www.canaan.com/companies"
MODAL_TMPL = "https://www.canaan.com/company/{slug}/modal"
SOURCE_URL = LIST_URL
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "canaan_companies.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
}
TIMEOUT = 45
RETRIES = 3

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify as _classify  # noqa: E402


def fetch(url, headers=None):
    last = None
    hdrs = headers or HEADERS
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=hdrs, timeout=TIMEOUT)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            last = e
            time.sleep(1.5 * attempt)
    raise SystemExit(f"FATAL: could not fetch {url}: {last}")


def clean(s):
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)
    s = unescape(s)
    s = re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()
    return s or None


def list_companies(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for a in soup.select("#company-list a.list-item, a.list-item[href*='/companies/']"):
        href = a.get("href") or ""
        m = re.search(r"/companies/([^/]+)/?$", href)
        if not m:
            continue
        slug = m.group(1)
        name_el = a.select_one("p")
        name = clean(name_el.get_text()) if name_el else None
        if not name:
            continue
        classes = " ".join(a.get("class") or [])
        status = "Current"
        if "acquired" in classes or "Acquired" in a.get_text():
            status = "Acquired"
        # Acquirer sometimes in the name suffix "Acquired by X"
        acquirer = None
        m2 = re.search(r"Acquired by (.+)$", name)
        if m2:
            acquirer = clean(m2.group(1))
            name = clean(name[: m2.start()])
            status = "Acquired"
        rows.append({
            "company_name": name,
            "slug": slug,
            "status": status,
            "acquirer": acquirer,
            "company_profile_url": f"https://www.canaan.com/companies/{slug}",
        })
    return rows


def parse_modal(js_text):
    """Modal response is jQuery that appends an HTML string — extract it."""
    info = {"description": None, "company_url": None, "partners": [], "stage": None, "logo_url": None}
    m = re.search(r'\.append\("(.+?)"\);\s*openCompanyModal', js_text, re.S)
    if not m:
        # try single-quoted
        m = re.search(r"\.append\('(.+?)'\);\s*openCompanyModal", js_text, re.S)
    if not m:
        return info
    raw = m.group(1)
    # Unescape JS string escapes
    raw = raw.replace("\\n", "\n").replace('\\"', '"').replace("\\/", "/").replace("\\'", "'")
    soup = BeautifulSoup(raw, "html.parser")
    h1 = soup.select_one("h1")
    # description: first <p> under content after h1
    for p in soup.find_all("p"):
        t = clean(p.get_text())
        if t and t not in {"Series A", "Series B", "Series C", "Series D", "Seed", "Growth"} and len(t) > 20:
            # skip bare stage labels
            if re.match(r"^(Series|Seed|Growth|Angel)", t) and len(t) < 30:
                continue
            info["description"] = t
            break
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http") and "canaan.com" not in href:
            info["company_url"] = clean(href)
            break
    # Investor links
    for a in soup.select('a[href*="/team/"]'):
        pn = clean(a.get("title") or a.get_text())
        if pn and pn not in info["partners"]:
            info["partners"].append(pn)
    # Investment stage: <h2>Investment</h2><p>Series A</p>
    for h2 in soup.find_all("h2"):
        if clean(h2.get_text()) == "Investment":
            nxt = h2.find_next("p")
            if nxt:
                info["stage"] = clean(nxt.get_text())
            break
    img = soup.select_one("img[src]")
    if img:
        info["logo_url"] = clean(img["src"])
    return info


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    skip_details = "--skip-details" in sys.argv
    html = fetch(LIST_URL, headers={k: v for k, v in HEADERS.items() if k != "X-Requested-With"})
    rows = list_companies(html)
    # dedupe by slug
    seen_slug, unique = set(), []
    for r in rows:
        if r["slug"] in seen_slug:
            continue
        seen_slug.add(r["slug"])
        unique.append(r)
    if limit:
        unique = unique[:limit]
    print(f"found {len(unique)} companies")

    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for i, r in enumerate(unique):
        description = company_url = stage = logo = None
        partners = []
        if not skip_details:
            try:
                modal = fetch(MODAL_TMPL.format(slug=r["slug"]))
                info = parse_modal(modal)
                description = info["description"]
                company_url = info["company_url"]
                partners = info["partners"]
                stage = info["stage"]
                logo = info["logo_url"]
                time.sleep(0.2)
            except Exception as e:
                print(f"  ! modal failed {r['slug']}: {e}", file=sys.stderr)
            if (i + 1) % 50 == 0:
                print(f"  modals {i + 1}/{len(unique)}")
        out.append({
            "company_name": r["company_name"],
            "description": description,
            "company_url": company_url,
            "company_profile_url": r["company_profile_url"],
            "logo_url": logo,
            "status": r["status"],
            "acquirer": r.get("acquirer"),
            "stage": stage,
            "partners": partners,
            "everywhere_tags": _classify(r["company_name"], description)[:4],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in ("description", "company_url", "logo_url", "stage", "status"):
        print(f"  {field}: {sum(1 for r in out if r.get(field))}/{n}")
    print(f"  status dist: {Counter(r['status'] for r in out)}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged ({len(untagged)} untagged)"
          + (f" -> {untagged[:20]}" if untagged else ""))
    tag_c = Counter(t for r in out for t in r["everywhere_tags"])
    for tag, cnt in tag_c.most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
