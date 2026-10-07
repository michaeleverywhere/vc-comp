#!/usr/bin/env python3
"""Qualcomm Ventures portfolio scraper -> qualcommventures_companies.json
Source: https://www.qualcommventures.com/portfolio/ — WordPress. The grid is
paged in client-side, so this reads the same `companies` posts from the
site's own WP REST API (/wp-json/wp/v2/companies, ~257 posts) plus its
sector / region / company-status taxonomies. Each post's rendered content
carries the website, Sectors, Investment Status (Active / Acquired / IPO),
Region, Investment Managers and the long description; the excerpt is the
short description.
Status: Active -> active, Acquired -> acquired, IPO -> active (listed; raw
kept in site_status).
"""
import html as htmllib, json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, label_after, html_text, clean_url, apply_tag_overrides

SOURCE_URL = "https://www.qualcommventures.com/portfolio/"
API = "https://www.qualcommventures.com/wp-json/wp/v2"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "qualcommventures_companies.json")
PRIMARY = "Qualcomm Ventures"
SECTOR_TAG_MAP = {
    "automotive": ["Transportation / Mobility"], "enterprise & data center": ["Dev Tools / Cloud"],
    "xr/metaverse": ["Deeptech / Robotics / AR/VR"], "consumer": ["Consumer"],
}


def terms(tax):
    out, page = {}, 1
    while True:
        d = fetch(f"{API}/{tax}?per_page=100&page={page}", as_json=True)
        for t in d:
            out[t["id"]] = clean(htmllib.unescape(t["name"]))
        if len(d) < 100:
            return out
        page += 1


def website_of(soup, label_text):
    cands = [a["href"].strip() for a in soup.select("a[href^=http]") if clean_url(a["href"])]
    lab = re.sub(r"\s+", "", label_text or "").lower()
    for u in cands:
        host = urlsplit(u).netloc.lower().removeprefix("www.")
        if host and host in lab:
            return clean_url(u)
    return clean_url(cands[0]) if cands else None


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Airspace": ["Dev Tools / Cloud", "Logistics / Supply Chain"],
    "Doctor on Demand": ["Health", "Consumer"],
    "Maketion": ["Dev Tools / Cloud"],
    "Workspot": ["Dev Tools / Cloud", "Cybersecurity"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    sectors_t, regions_t, status_t = terms("sector"), terms("region"), terms("company-status")
    posts, page = [], 1
    while True:
        d = fetch(f"{API}/companies?per_page=100&page={page}", as_json=True)
        posts += d
        if len(d) < 100 or (limit and len(posts) >= limit):
            break
        page += 1
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for p in posts:
        name = clean(htmllib.unescape(p["title"]["rendered"]))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        soup = BeautifulSoup(p["content"]["rendered"], "html.parser")
        st = [s.strip() for s in soup.stripped_strings]
        try:
            i = st.index("Sectors")
        except ValueError:
            i = 1
        url = website_of(soup, "".join(st[1:i]))
        managers = []
        if "Investment Managers" in st:
            for s in st[st.index("Investment Managers") + 1:]:
                if len(s) > 60 or s in ("Related Articles",):
                    break
                managers.append(clean(s))
        long_desc = next((clean(s) for s in st[i:] if len(s) > 60), None)
        sectors = [sectors_t[x] for x in p.get("sector") or [] if x in sectors_t]
        regions = [regions_t[x] for x in p.get("region") or [] if x in regions_t]
        stt = [status_t[x] for x in p.get("company-status") or [] if x in status_t]
        stt = stt[0] if stt else label_after(st, "Investment Status")
        short = html_text(p.get("excerpt", {}).get("rendered"))
        out.append({
            "company_name": name,
            "description": short or long_desc,
            "long_description": long_desc if long_desc and long_desc != short else None,
            "company_url": url,
            "company_profile_url": p.get("link"),
            "status": {"active": "active", "acquired": "acquired", "ipo": "active"}.get((stt or "").lower()),
            "site_status": stt,
            "location": ", ".join(regions) or None,
            "sectors": sectors,
            "investment_managers": managers,
            "everywhere_tags": tags_for(name, short or long_desc, [s for s in sectors if s not in ("AI", "5G", "IoT")], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "long_description", "company_url", "status", "location", "sectors", "investment_managers", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
