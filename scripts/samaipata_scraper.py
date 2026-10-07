#!/usr/bin/env python3
"""Samaipata portfolio scraper -> samaipata_companies.json
Source: https://www.samaipata.vc/our-portfolio — Webflow (Finsweet filters);
all company cards are server-rendered (name, description, geography and the
portfolio stage bucket Seed / Early / Growth / Exited / N/A, which is not a
funding round). Each /portfolio-companies/<slug> page adds the tagline,
Founders, Headquarters, Year invested, Other key investors, Money raised
(as published, e.g. ">€30m") and Status (e.g. "Live"), plus the website.
Status: Live -> active; Exited (card bucket or page status) -> acquired.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, label_after, first_external_link, clean_url, apply_tag_overrides

SOURCE_URL = "https://www.samaipata.vc/our-portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "samaipata_companies.json")
PRIMARY = "Samaipata"
OWN = ("samaipata.vc", "getro.com", "docsend.com", "typeform.com", "personiowhistleblowing.com", "drive.google.com")
LABELS = ("Founders", "Headquarters", "Year invested", "Other key investors", "Money raised", "Status")


def block(strings, label):
    """Values between a label and the next known label."""
    if label not in strings:
        return []
    i = strings.index(label) + 1
    vals = []
    while i < len(strings) and strings[i] not in LABELS and strings[i] != "OUR\xa0PORTFOLIO" and strings[i] != "OUR PORTFOLIO":
        vals.append(strings[i])
        i += 1
    return vals


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Big blue": ["Logistics / Supply Chain"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards, seen = [], set()
    for it in soup.select(".portfolio-company-card-wide"):
        a = it.select_one("a[href]")
        prof = urljoin(SOURCE_URL, a["href"]) if a else None
        f = {x.get("fs-cmsfilter-field") or x.get("fs-cmssort-field"): clean(x.get_text(" "))
             for x in it.select("[fs-cmsfilter-field], [fs-cmssort-field]")}
        name = f.get("name")
        d = it.select_one(".text-style-2lines")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        cards.append((name, prof, clean(d.get_text(" ")) if d else None, f))
        if limit and len(cards) >= limit:
            break
    details = fetch_many([c[1] for c in cards if c[1]])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for name, prof, desc, f in cards:
        page = {}
        h = details.get(prof)
        if h:
            s = BeautifulSoup(h, "html.parser")
            for t in s(["script", "style", "svg"]):
                t.decompose()
            st = [clean(x.replace("\u200d", "")) for x in s.body.stripped_strings if clean(x.replace("\u200d", ""))]
            page = {lab: block(st, lab) for lab in LABELS}
            if "Founders" in st:
                i = st.index("Founders")
                page["tagline"] = st[i - 2] if i >= 2 and st[i - 1] == desc else None
            page["site"] = clean_url(first_external_link(s, OWN))
        raw_status = (page.get("Status") or [None])[0]
        bucket = f.get("Stage")
        if (raw_status or "").lower() in ("live", "active"):
            status = "active"
        elif (raw_status or "").lower() in ("exited", "acquired") or (bucket or "").lower() == "exited":
            status = "acquired"
        else:
            status = None
        year = (page.get("Year invested") or [None])[0]
        investors = (page.get("Other key investors") or [None])[0]
        out.append({
            "company_name": name,
            "description": desc,
            "tagline": page.get("tagline"),
            "company_url": page.get("site"),
            "company_profile_url": prof,
            "status": status,
            "site_status": raw_status or (bucket if bucket == "Exited" else None),
            "portfolio_stage": bucket,
            "first_invested": year if year and re.fullmatch(r"\d{4}", year) else None,
            "location": (page.get("Headquarters") or [None])[0] or f.get("Geography"),
            "country": f.get("Geography"),
            "founders": page.get("Founders") or [],
            "other_key_investors": [clean(x) for x in investors.split(",")] if investors else [],
            "total_raised": next((v for v in page.get("Money raised") or [] if v.upper() != "N/A"), None),
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "first_invested", "location", "founders", "total_raised", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
