#!/usr/bin/env python3
"""
Craft Ventures portfolio scraper -> craft_companies.json

Source: Webflow CMS list on https://www.craftventures.com/portfolio
(`.company-wrapper .portfolio-card` items). Structured nodes:
  .portfolio-name-holder .text-size-medium = name
  .exit = exited chip
  p.text-color-yellow = exit detail (IPO/acquired date)
  p.text-size-tiny (non-yellow) = description
  .investors-holder p = partners
  .stage-holder p = stage
  a.card-link-block = company_url

Highlights swiper is skipped (subset of the same companies).

usage:
    python3 scripts/craft_scraper.py [--limit N]
"""
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.craftventures.com/portfolio"
SOURCE_URL = PORTFOLIO_URL
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "craft_companies.json")
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

def craft_tags(name, description):
    tags = _classify(name, description)
    text = f"{name or ''} {description or ''}".lower()
    extras = []
    if any(k in text for k in ("lender", "buy-now-pay-later", "bnpl", "pay-later", "installment")):
        extras.append("FinTech / Insurance")
    if any(k in text for k in ("scooter", "ride-share", "rideshare", "micromobility")):
        extras.append("Transportation / Mobility")
    out = []
    for x in extras + tags:
        if x not in out:
            out.append(x)
    return out[:4]


def fetch(url):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
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
    s = re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()
    return s or None


def parse_card(it):
    card = it.select_one(".portfolio-card") or it
    name_el = card.select_one(".portfolio-name-holder .text-size-medium")
    name = clean(name_el.get_text()) if name_el else None
    if not name:
        return None
    # Skip junk if a stage label leaked in
    if name.lower() in {"series", "angel", "seed", "stage"}:
        return None

    status = "Exited" if card.select_one(".exit") else "Active"
    exit_detail = None
    # Webflow leaves an empty yellow <p class="... w-dyn-bind-empty"> on every
    # card; only a non-empty yellow paragraph is a real exit detail.
    yellow = card.select_one("p.text-color-yellow")
    if yellow:
        yd = clean(yellow.get_text())
        if yd:
            exit_detail = yd
            status = "Exited"

    description = None
    for p in card.select(".portfolio-content-holder p.text-size-tiny"):
        if "text-color-yellow" in (p.get("class") or []):
            continue
        t = clean(p.get_text())
        if t and len(t) >= 15:
            description = t
            break

    partners = []
    for p in card.select(".investors-holder p"):
        pn = clean(p.get_text())
        if pn and pn not in partners:
            partners.append(pn)

    stage = None
    stages = [clean(p.get_text()) for p in card.select(".stage-holder p")]
    stages = [s for s in stages if s]
    if stages:
        stage = ", ".join(stages)

    company_url = None
    a = card.select_one("a.card-link-block[href], a[href^='http']")
    if a and a.get("href", "").startswith("http"):
        href = a["href"]
        if not any(x in href for x in ("craftventures", "linkedin", "twitter", "x.com", "youtube", "medium")):
            company_url = clean(href)

    logo = None
    img = card.select_one("img.company-logo")
    if img and img.get("src"):
        logo = clean(img["src"])

    year = None
    # Not present on logo-grid cards; highlights carry "Invested YYYY"

    return {
        "company_name": name,
        "description": description,
        "company_url": company_url,
        "logo_url": logo,
        "status": status,
        "exit_detail": exit_detail,
        "stage": stage,
        "partners": partners,
        "everywhere_tags": craft_tags(name, description),
        "source_url": SOURCE_URL,
    }


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(PORTFOLIO_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()

    cards = []
    wrap = soup.select_one(".company-wrapper .w-dyn-items")
    if wrap:
        cards = wrap.select(":scope > .w-dyn-item")

    out, seen = [], set()
    for it in cards:
        rec = parse_card(it)
        if not rec:
            continue
        key = rec["company_name"].lower()
        if key in seen:
            continue
        seen.add(key)
        rec["scraped_at"] = scraped_at
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in ("description", "company_url", "logo_url", "stage", "exit_detail"):
        print(f"  {field}: {sum(1 for r in out if r.get(field))}/{n}")
    print(f"  partners: {sum(1 for r in out if r['partners'])}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged ({len(untagged)} untagged)"
          + (f" -> {untagged[:20]}" if untagged else ""))
    tag_c = Counter(t for r in out for t in r["everywhere_tags"])
    for tag, cnt in tag_c.most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
