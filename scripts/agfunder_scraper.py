#!/usr/bin/env python3
"""AgFunder portfolio scraper -> agfunder_companies.json
Source: https://agfunder.com/portfolio/ — WordPress archive paginated as
/portfolio/page/N/. Each <article class="portfolio-item"> has the name (with
an "[EXITED]" suffix for exits), a one-line tagline and a detail link. Detail
pages add region and sector labels (the two short labels under the title) and
a "Summary" paragraph (used as description). location = that region label
(the only geography AgFunder publishes). status: "[EXITED]" kept as
site_status "Exited" (AgFunder does not say acquired); no lead status. No
round or year published. AgFunder invests in agrifood / climate tech.
"""
import os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch_many, clean, tags_for, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out
import requests
from _scraper_common import HEADERS

SOURCE_URL = "https://agfunder.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "agfunder_companies.json")
PRIMARY = "AgFunder"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "climate": ["Climate / Sustainability"], "food": ["CPG"],
    "supply chain": ["Logistics / Supply Chain"], "robotics & automation": ["Deeptech / Robotics / AR/VR"],
    "energy": ["Climate / Sustainability"],
    "biotech": ["BioTech"], "health": ["Health"],
}
TAG_OVERRIDES = {}
REGIONS = {"uk/europe", "south america", "asia", "north america", "europe", "latin america", "africa", "middle east", "oceania", "global", "india", "israel"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows, seen, page = [], set(), 1
    while page < 40:
        url = SOURCE_URL if page == 1 else f"{SOURCE_URL}page/{page}/"
        r = requests.get(url, headers=HEADERS, timeout=45)
        if r.status_code == 404:
            break
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        arts = soup.select("article.portfolio-item")
        if not arts:
            break
        for art in arts:
            a = art.select_one(".article-title a[href]")
            if not a or a["href"] in seen:
                continue
            seen.add(a["href"])
            raw = clean(a.get_text(" "))
            exited = bool(re.search(r"\[\s*exit(ed)?\s*\]", raw or "", re.I))
            name = clean(re.sub(r"\[\s*exit(ed)?\s*\]", "", raw or "", flags=re.I))
            tg = art.select_one(".article-tagline")
            rows.append({"name": name, "href": a["href"], "exited": exited,
                         "tagline": clean(tg.get_text(" ")) if tg else None})
        page += 1
    pages = fetch_many([r["href"] for r in rows], workers=4)
    out, names = [], set()
    for r in rows:
        if not r["name"] or r["name"].lower() in names:
            continue
        names.add(r["name"].lower())
        summary, region, sectors = None, None, []
        html = pages.get(r["href"])
        if html:
            d = BeautifulSoup(html, "html.parser")
            for t in d(["script", "style", "nav", "footer", "header"]):
                t.decompose()
            strings = [clean(s) for s in d.stripped_strings]
            strings = [s for s in strings if s]
            if "Summary" in strings:
                i = strings.index("Summary")
                labels = [s for s in strings[max(0, i - 4):i] if len(s) < 40 and "[" not in s and s != r["name"]]
                for l in labels:
                    if l.lower() in REGIONS:
                        region = l
                    elif l not in ("Back", "Menu"):
                        sectors.append(l)
                parts = []
                for s in strings[i + 1:i + 6]:
                    if s in ("Why We Invested", "Team", "Founders"):
                        break
                    parts.append(s)
                summary = clean(" ".join(parts)) or None
        out.append({
            "company_name": r["name"],
            "description": summary or r["tagline"],
            "tagline": r["tagline"],
            "sectors": sectors,
            "region": region,
            "location": region,  # AgFunder publishes only a region (e.g. North America / Asia)
            "site_status": "Exited" if r["exited"] else None,
            "everywhere_tags": tags_for(r["name"], " ".join(x for x in (r["tagline"], summary) if x), sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": r["href"],
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "sectors", "region", "site_status", "everywhere_tags"))


if __name__ == "__main__":
    main()
