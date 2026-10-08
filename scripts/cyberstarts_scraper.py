#!/usr/bin/env python3
"""Cyberstarts portfolio scraper -> cyberstarts_companies.json
Source: https://www.cyberstarts.com/portfolio — Webflow CMS grid
(server-rendered, Finsweet list status field Active / Exited) linking to
/companies/<slug> detail pages. Per detail page: website, description,
team (founders), and the Milestones block (Founded / Partnered / Acquired:
<year> by <acquirer>). Partnered year -> first_invested.
Status: Active -> active; Exited -> acquired (raw kept in site_status).
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, first_external_link, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.cyberstarts.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "cyberstarts_companies.json")
PRIMARY = "Cyberstarts"
OWN = ("cyberstarts.com", "website-files.com", "webflow")

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "A Security": ["Cybersecurity"],
    "Bionic": ["Cybersecurity", "Dev Tools / Cloud"],
    "Cyera": ["Cybersecurity", "Data & Analytics"],
    "Gambit": ["Cybersecurity"],
    "Legit": ["Cybersecurity", "Dev Tools / Cloud"],
    "Linx": ["Cybersecurity"],
    "NewCore": ["Cybersecurity"],
    "Oasis": ["Cybersecurity", "Dev Tools / Cloud"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards, seen = [], set()
    for it in soup.select(".companies-grid_citem"):
        c = it.select_one(".companies-grid_content:not(.w-condition-invisible)") or it.select_one(".companies-grid_content")
        inner = c.find("div").find("div") if c and c.find("div") else None
        name = clean(inner.get_text(" ")) if inner else None
        tagline = clean(c.select_one(".text-opacity-60").get_text(" ")) if c and c.select_one(".text-opacity-60") else None
        a = it.select_one("a.media_item-link[href]") or it.select_one('a[href^="/companies/"]')
        st = it.select_one('[fs-list-field="status"]')
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        cards.append((name, tagline, urljoin(SOURCE_URL, a["href"]) if a else None, clean(st.get_text()) if st else None))
        if limit and len(cards) >= limit:
            break
    details = fetch_many([c[2] for c in cards if c[2]])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for name, tagline, prof, raw_status in cards:
        desc = site = founded = partnered = acq_year = acquirer = None
        team = []
        h = details.get(prof)
        if h:
            s = BeautifulSoup(h, "html.parser")
            for t in s(["script", "style", "svg", "nav", "footer"]):
                t.decompose()
            st = [clean(x) for x in s.body.stripped_strings if clean(x)]
            site = clean_url(first_external_link(s, OWN, extra_skip=("/press/", "/news/", "/blog/")))
            # description: rich-text paragraphs, skipping partner quotes
            rt = s.select_one(".w-richtext")
            paras = [clean(p.get_text()) for p in rt.select("p")] if rt else []
            paras = [p for p in paras if p and not p.startswith(("\u201c", '"'))]
            desc = " ".join(paras[:2]) or None
            if "Team" in st and "Milestones" in st:
                team = st[st.index("Team") + 1:st.index("Milestones")]
            for x in st:
                m = re.match(r"Founded:\s*(\d{4})", x)
                founded = founded or (int(m.group(1)) if m else None)
                m = re.match(r"Partnered:\s*(\d{4})", x)
                partnered = partnered or (int(m.group(1)) if m else None)
                m = re.match(r"Acquired:\s*(\d{4})?\s*(?:by\s+(.+))?", x)
                if m and (m.group(1) or m.group(2)):
                    acq_year, acquirer = (int(m.group(1)) if m.group(1) else None), clean(m.group(2))
        status = {"active": "active", "exited": "acquired"}.get((raw_status or "").lower())
        if acquirer:
            status = "acquired"
        full = desc or tagline
        out.append({
            "company_name": name,
            "description": full,
            "tagline": tagline,
            "company_url": site,
            "company_profile_url": prof,
            "status": status,
            "site_status": raw_status,
            "acquirer": acquirer,
            "exit_year": acq_year,
            "year_founded": founded,
            "first_invested": partnered,
            "founders": team,
            "everywhere_tags": tags_for(name, " ".join(x for x in (tagline, desc) if x)),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, None)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "first_invested", "founders", "acquirer", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
