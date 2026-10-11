#!/usr/bin/env python3
"""5AM Ventures portfolio scraper -> fiveam_companies.json
Source: https://5amventures.com/portfolio/ — WordPress page; each company is an
<li class="company-click"> with data-title, data-desc (HTML blurb), data-website,
data-team (5AM partners), data-groups ("active" / "acquired-ipos") and data-facts
(<li> list: "Founded in YYYY", "IPO in <Month YYYY>", "Acquired in <Month YYYY>",
"Based in <City, ST>", "Therapeutic Focus: ..."). Location = "Based in" fact.
status: "acquired" only when a fact says "Acquired in"; "active" when the site
groups it as active; IPO-only exits kept as site_status "IPO" (status blank).
No funding round or investment year published.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, html_text, tags_for, clean_url, year_of,
                             prune_substring_tags, apply_tag_overrides)

SOURCE_URL = "https://5amventures.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "fiveam_companies.json")
PRIMARY = "5AM Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "Cabaletta Bio": ["BioTech"],
    "Calibrium": ["BioTech", "Health"],
    "Neurogastrx": ["BioTech"],
    "Renasant Bio": ["BioTech"],
    "Rennovia": ["Climate / Sustainability"],
    "Synosia": ["BioTech"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for c in soup.select("li.company-click[data-title]"):
        name = clean(c.get("data-title"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = html_text(c.get("data-desc") or "")
        facts = [clean(li.get_text(" ")) for li in BeautifulSoup(c.get("data-facts") or "", "html.parser").select("li")]
        facts = [f for f in facts if f]
        loc = next((f[len("Based in"):].strip() for f in facts if f.lower().startswith("based in")), None)
        focus = next((f.split(":", 1)[1].strip() for f in facts if f.lower().startswith("therapeutic focus")), None)
        founded = next((year_of(f) for f in facts if f.lower().startswith("founded")), None)
        acquired = any(f.lower().startswith("acquired") for f in facts)
        ipo = any(f.lower().startswith("ipo") for f in facts)
        grp = (c.get("data-groups") or "").strip()
        status = "acquired" if acquired else ("active" if grp == "active" else None)
        site_status = "Acquired" if acquired else ("IPO" if ipo else ("Active" if grp == "active" else None))
        team = [clean(x) for x in re.split(r",|<br\s*/?>", html_text(c.get("data-team") or "") or "") if clean(x)]
        sectors = [focus] if focus else []
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": clean_url(c.get("data-website")),
            "sectors": sectors,
            "location": loc,
            "founded_year": founded,
            "status": status,
            "site_status": site_status,
            "facts": facts,
            "fiveam_team": team,
            "everywhere_tags": tags_for(name, " ".join(x for x in (desc, focus) if x), sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "location", "founded_year", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
