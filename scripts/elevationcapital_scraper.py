#!/usr/bin/env python3
"""Elevation Capital portfolio scraper -> elevationcapital_companies.json
Source: https://www.elevationcapital.com/portfolio — Next.js page whose
__NEXT_DATA__ embeds every portfolioCompany document (Elevation's own Sanity
CMS): title, short_description, bio (long text), founders, stageType
(investing stage: Seed / Series A / Growth / Public), sector tags and a
"Visit <company> website" link.
Stage: Seed / Series A kept as funding round; "Growth" is not a named round ->
stage null (raw kept in investing_stage). "Public" -> status active (listed),
stage null. No other status is published.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, stage_label, clean_url, apply_tag_overrides

SOURCE_URL = "https://www.elevationcapital.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "elevationcapital_companies.json")
PRIMARY = "Elevation Capital"
SECTOR_TAG_MAP = {
    "consumer tech": ["Consumer"], "consumer brands": ["CPG", "Consumer"],
    "fintech & financial services": ["FinTech / Insurance"], "frontier tech": ["Deeptech / Robotics / AR/VR"],
    "healthcare": ["Health"],
}


def blocks_text(v):
    if not v:
        return None
    parts = []
    for b in v.get("text") if isinstance(v, dict) else v:
        for c in (b or {}).get("children") or []:
            parts.append(c.get("text") or "")
        parts.append(" ")
    return clean("".join(parts))


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Treebo": ["Consumer"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    data = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S).group(1))
    companies = []
    for sl in data["props"]["pageProps"]["data"]["page"]["slices"]:
        if isinstance(sl, dict) and sl.get("portfolios"):
            companies += sl["portfolios"]
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for p in companies:
        name = clean(p.get("title"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        url = None
        for l in p.get("links") or []:
            for c in l.get("cta_link") or []:
                u = clean_url(c.get("url"))
                if u and not url:
                    url = u
        st = (p.get("stageType") or {}).get("title")
        sectors = [t["title"] for t in p.get("tags") or [] if t.get("title")]
        desc = clean(p.get("short_description"))
        bio = blocks_text(p.get("bio"))
        out.append({
            "company_name": name,
            "description": desc or bio,
            "long_description": bio if desc else None,
            "company_url": url,
            "company_profile_url": f"https://www.elevationcapital.com/portfolio/{p['slug']}" if p.get("slug") else None,
            "investing_stage": st,
            "stage": stage_label(st),
            "status": "active" if (st or "").lower() == "public" else None,
            "founders": [clean(f.get("title") if isinstance(f, dict) else f) for f in p.get("founders") or [] if clean(f.get("title") if isinstance(f, dict) else f)],
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc or bio, sectors, SECTOR_TAG_MAP),
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
    for k in ("description", "long_description", "company_url", "stage", "status", "founders", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
