#!/usr/bin/env python3
"""Salesforce Ventures portfolio scraper -> salesforceventures_companies.json
Source: https://salesforceventures.com/portfolio/ — WordPress. The grid is fed
by the site's own public WP REST collection /wp-json/wp/v2/companies (621
companies) with taxonomies company_status (Active / Exited / Spotlight),
company_type (industry focus areas) and company_region (AMER / EMEA / APAC).
Each company page (/companies/<slug>/) adds the website link, Leadership and a
"Status" line (Private / Public / Acquired ...).
status: company_status Active -> active; Exited + "Acquired" status text ->
acquired. Region is a sales region, kept as `region` (not a location).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, html_text, tags_for, clean_url, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://salesforceventures.com/portfolio/"
API = "https://salesforceventures.com/wp-json/wp/v2/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "salesforceventures_companies.json")
PRIMARY = "Salesforce Ventures"
SECTOR_TAG_MAP = {
    "future of work": ["Future of Work"], "security": ["Cybersecurity"], "data stack": ["Data & Analytics"],
    "fintech": ["FinTech / Insurance"], "health tech": ["Health"], "commerce": ["Consumer"],
    "defense": ["RegTech/Gov/Legal"], "impact": ["Climate / Sustainability"],
}
TAG_OVERRIDES = {}


def terms(tax):
    return {t["id"]: t["name"] for t in fetch(API + tax + "?per_page=100", as_json=True)}


def _merge_duplicates(records):
    """The CMS holds some companies twice (`<slug>` and `<slug>-2`). Merge
    entries with the same name AND the same website domain, keeping the first
    and filling its empty fields from the duplicate. Same-name entries with
    different or missing websites are left separate (could be different
    companies)."""
    import re as _re
    from urllib.parse import urlparse as _up
    def key(r):
        host = _up(r.get("company_url") or "").netloc.lower().removeprefix("www.")
        return ((r.get("company_name") or "").strip().lower(), host) if host else None
    seen, merged = {}, []
    for r in records:
        k = key(r)
        if k and k in seen:
            keep = seen[k]
            for f, v in r.items():
                if v and not keep.get(f):
                    keep[f] = v
            keep.setdefault("duplicate_profile_urls", []).append(r.get("profile_url"))
            continue
        if k:
            seen[k] = r
        merged.append(r)
    return merged


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    st_t, ty_t, rg_t = terms("company_status"), terms("company_type"), terms("company_region")
    items, page = [], 1
    while True:
        batch = fetch(API + f"companies?per_page=100&page={page}&_fields=id,slug,link,title,content,company_status,company_type,company_region", as_json=True)
        items += batch
        if len(batch) < 100:
            break
        page += 1
    if limit:
        items = items[:limit]
    pages = fetch_many([i["link"] for i in items], workers=8)
    out, seen = [], set()
    for i in items:
        name = html_text(i["title"]["rendered"])
        if not name or i["link"] in seen:
            continue
        seen.add(i["link"])
        desc = html_text(i["content"]["rendered"])
        statuses = [st_t.get(x) for x in i.get("company_status") or [] if st_t.get(x)]
        types = [ty_t.get(x) for x in i.get("company_type") or [] if ty_t.get(x)]
        regions = [rg_t.get(x) for x in i.get("company_region") or [] if rg_t.get(x)]
        site, status_text, leadership = None, None, []
        html = pages.get(i["link"])
        if html:
            d = BeautifulSoup(html, "html.parser")
            a = d.select_one("a.profile__link[href]")
            site = clean_url(a["href"]) if a else None
            for h3 in d.select("h3.profile-more-info-subtitle"):
                box = h3.find_next_sibling("div", class_="profile-more-info")
                if not box:
                    continue
                lab = clean(h3.get_text(" "))
                if lab == "Status":
                    status_text = clean(box.get_text(" "))
                elif lab == "Leadership":
                    leadership = [clean(x) for x in box.get_text("\n").split("\n") if clean(x)]
            if not desc:
                p = d.select_one("section.profile-info > p")
                desc = clean(p.get_text(" ")) if p else None
        stx = (status_text or "").lower()
        acquirer = None
        m = re.match(r"(?i)acquired(?: by)?\s*:?\s*(.*)$", status_text or "")
        if m:
            acquirer = clean(m.group(1))
        if "Active" in statuses and not stx.startswith("acquired"):
            status = "active"
        elif stx.startswith("acquired"):
            status = "acquired"
        else:
            status = None
        sectors = [t for t in types if t != "Slack Fund"]
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": site,
            "focus_areas": types,
            "region": regions[0] if len(regions) == 1 else (", ".join(regions) or None),
            "portfolio_status": [s for s in statuses if s != "Spotlight"],
            "status_text": status_text,
            "status": status,
            "acquirer": acquirer,
            "leadership": leadership,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": i["link"],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    out = _merge_duplicates(out)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "focus_areas", "region", "status_text", "status", "acquirer", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
