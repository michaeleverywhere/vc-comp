#!/usr/bin/env python3
"""
Lowercarbon Capital portfolio scraper -> lowercarbon_companies.json

Source: WordPress REST API
  GET https://lowercarbon.com/wp-json/wp/v2/company?per_page=100&page=N
(~101 companies). Description / founded / HQ / website are parsed from
content.rendered HTML. Profile URL is the WP permalink.

usage:
    python3 scripts/lowercarbon_scraper.py [--limit N]
"""
import html as htmlmod
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

API = "https://lowercarbon.com/wp-json/wp/v2/company"
SOURCE_URL = "https://lowercarbon.com/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "lowercarbon_companies.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 45
RETRIES = 3

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify as _classify  # noqa: E402


def get_json(url, params=None):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            return r, r.json()
        except requests.RequestException as e:
            last = e
            time.sleep(1.5 * attempt)
    raise SystemExit(f"FATAL: could not fetch {url}: {last}")


def clean(s):
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)
    s = htmlmod.unescape(s)
    s = re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()
    return s or None


def parse_content(rendered):
    """Pull description, founded year, HQ, company website from block HTML."""
    info = {"description": None, "year_founded": None, "location": None, "company_url": None}
    if not rendered:
        return info
    soup = BeautifulSoup(rendered, "html.parser")
    text = soup.get_text("\n", strip=True)
    # Founded: YYYY
    m = re.search(r"Founded:\s*(\d{4})", text)
    if m:
        info["year_founded"] = m.group(1)
    m = re.search(r"HQ:\s*([^\n]+)", text)
    if m:
        info["location"] = clean(m.group(1))
    # External website: first non-lowercarbon, non-press link, or bare domain line
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("http"):
            continue
        if any(x in href for x in ("lowercarbon", "nytimes.com", "axios.com", "techcrunch",
                                    "bloomberg.com", "wsj.com", "linkedin.com", "twitter.com", "x.com")):
            continue
        info["company_url"] = clean(href)
        break
    # Description: prefer the short blurb near the top ("The grid's battery...")
    # Heuristic: first paragraph after HQ/domain that is 40-300 chars and not a section header
    skip = {"big picture", "the problem", "the solution", "why now", "team", "press"}
    paragraphs = [clean(p.get_text(" ", strip=True)) for p in soup.find_all("p")]
    paragraphs = [p for p in paragraphs if p]
    for p in paragraphs:
        if p.lower() in skip:
            continue
        if re.match(r"^(Founded:|HQ:|Slashing)", p):
            continue
        if 25 <= len(p) <= 400:
            info["description"] = p
            break
    # Fallback: "About"-adjacent or longest mid-length paragraph
    if not info["description"]:
        for p in paragraphs:
            if 40 <= len(p) <= 600 and p.lower() not in skip:
                info["description"] = p
                break
    return info


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    page, out, seen = 1, [], set()
    scraped_at = datetime.now(timezone.utc).isoformat()
    while True:
        r, data = get_json(API, params={"per_page": 100, "page": page})
        if not data:
            break
        for item in data:
            name = clean((item.get("title") or {}).get("rendered"))
            if not name or name in seen:
                continue
            seen.add(name)
            parsed = parse_content((item.get("content") or {}).get("rendered"))
            # Climate firm — seed Climate tag, then keyword-classify
            tags = _classify(name, parsed["description"], ["Climate", "Sustainability"])
            if "Climate / Sustainability" not in tags:
                tags = ["Climate / Sustainability"] + tags
            tags = tags[:4]
            out.append({
                "company_name": name,
                "description": parsed["description"],
                "company_url": parsed["company_url"],
                "company_profile_url": clean(item.get("link")),
                "location": parsed["location"],
                "year_founded": parsed["year_founded"],
                "everywhere_tags": tags,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
            if limit and len(out) >= limit:
                break
        if limit and len(out) >= limit:
            break
        total_pages = int(r.headers.get("X-WP-TotalPages") or "1")
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.3)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in ("description", "company_url", "company_profile_url", "location", "year_founded"):
        print(f"  {field}: {sum(1 for r in out if r.get(field))}/{n}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged ({len(untagged)} untagged)"
          + (f" -> {untagged[:20]}" if untagged else ""))
    tag_c = Counter(t for r in out for t in r["everywhere_tags"])
    for tag, cnt in tag_c.most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
