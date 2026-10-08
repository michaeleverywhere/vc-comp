#!/usr/bin/env python3
"""Maveron portfolio scraper -> maveron_companies.json
Source: https://www.maveron.com/portfolio — Webflow CMS (Finsweet filters),
server-rendered. Companies are grouped under "active" and "exits" headers;
each hover item carries the name, category (Commerce / FinTech / Health ...),
website, Maveron investors and, for exits, a note such as "NASDAQ: BIRD" or
"Acquired by ...". The site publishes no descriptions, stage, location or
investment year (descriptions may later be filled from company websites by
scripts/fill_descriptions_web.py, never invented).
Status: active group -> active; exits with "Acquired by" -> acquired; other
exits (IPO / ticker) keep the raw note in exit_detail and status blank.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, carry_forward_descriptions, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.maveron.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "maveron_companies.json")
PRIMARY = "Maveron"
SECTOR_TAG_MAP = {
    "commerce": ["Consumer"], "fintech": ["FinTech / Insurance"], "health": ["Health"],
    "education": ["Future of Work"], "hr": ["Future of Work"], "energy": ["Climate / Sustainability"],
    "social": ["Consumer"], "gaming": ["Gaming / Media / Entertainment"], "media": ["Gaming / Media / Entertainment"],
    "real estate": ["PropTech"], "travel": ["Consumer"], "food": ["CPG"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Common": ["PropTech"],
    "Landing": ["PropTech", "Consumer"],
    "Pacaso": ["PropTech", "Consumer"],
    "The Guild": ["PropTech"],
    "Trupanion": ["FinTech / Insurance", "Consumer"],
    "WeatherPromise": ["FinTech / Insurance", "Consumer"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for grp in soup.select(".portfolio-group"):
        hdr = grp.select_one(".portfolio-group-header")
        group = clean(hdr.get_text(" ")).lower() if hdr else None
        for it in grp.select(".exit-hover-item"):
            n = it.select_one(".portfolio-group-item-copy") or it.select_one(".portfolio-group-item")
            name = clean(n.get_text(" ")) if n else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            cats = []
            for c in it.select('[fs-cmsfilter-field="category"]'):
                v = clean(c.get_text(" "))
                if v and v != "All" and v not in cats:
                    cats.append(v)
            rt = it.select_one(".notable-rich-text")
            site, investors, notes = None, [], []
            if rt:
                for p in rt.select("p"):
                    lab = p.select_one("strong")
                    label = clean(lab.get_text(" ")) if lab else None
                    if label == "Website":
                        a = p.select_one("a[href]")
                        site = a["href"] if a else None
                    elif label == "Investors":
                        lab.decompose()
                        investors = [clean(x) for x in p.stripped_strings if clean(x) and clean(x) != "\u200d"]
                    else:
                        v = clean(p.get_text(" ").replace("\u200d", ""))
                        if v:
                            notes.append(v)
            if not site:
                a = it.select_one("a[href^=http]")
                site = a["href"] if a else None
            note = "; ".join(notes) or None
            acq = re.search(r"(?i)acquired by\s+(.+)", note or "")
            acquirer = exit_year = None
            if acq:
                am = re.match(r"(.+?),?\s*((?:19|20)\d{2})?\.?$", clean(acq.group(1)))
                acquirer, exit_year = clean(am.group(1)), (int(am.group(2)) if am.group(2) else None)
                # exits often link to the acquirer's site, which is not the company website
                key = re.sub(r"[^a-z0-9]", "", acquirer.lower().split()[0]) if acquirer else ""
                if site and key and key in re.sub(r"[^a-z0-9.]", "", site.lower()):
                    site = None
            if group == "active":
                status = "active"
            elif acq:
                status = "acquired"
            else:
                status = None
            out.append({
                "company_name": name,
                "description": None,
                "company_url": clean_url(site),
                "status": status,
                "site_status": group,
                "exit_detail": note if group != "active" else None,
                "acquirer": acquirer,
                "exit_year": exit_year,
                "sectors": cats,
                "partners": investors,
                "everywhere_tags": tags_for(name, None, cats, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
            if limit and len(out) >= limit:
                break
    for r in carry_forward_descriptions(out, OUT):
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"], r["sectors"], SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "exit_detail", "acquirer", "sectors", "partners", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
