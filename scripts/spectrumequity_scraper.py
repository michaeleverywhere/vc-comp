#!/usr/bin/env python3
"""Spectrum Equity portfolio scraper -> spectrumequity_companies.json
Source: https://www.spectrumequity.com/portfolio — Nuxt prerender payloads:
/portfolio/_payload.json (97 companies: name, headline, status, sectors, themes,
regions, exit scenario) + each /portfolio/<slug>/_payload.json (headquarters,
partnership year, website, CEO).
"""
import os, re, sys, json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, fetch_many, prune_substring_tags, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.spectrumequity.com/portfolio"
BASE = "https://www.spectrumequity.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "spectrumequity_companies.json")
PRIMARY = "Spectrum Equity"
SECTOR_TAG_MAP = {
    "consumer": ["Consumer"], "healthcare technology": ["Health"], "financial technology": ["FinTech / Insurance"],
    "education technology": [], "enterprise software": [], "marketing technology": [],
    "data & analytics": ["Data & Analytics"], "data and analytics": ["Data & Analytics"],
    "security": ["Cybersecurity"], "government technology": ["RegTech/Gov/Legal"],
    "healthcare information technology": ["Health"], "insurance tech": ["FinTech / Insurance"],
    "legal technology": ["RegTech/Gov/Legal"], "transportation & logistics": ["Logistics / Supply Chain"],
    "media & telecommunications": ["Gaming / Media / Entertainment"], "risk management": [],
    "marketing & sales technology": [], "smb software": [], "travel & hospitality": [], "productivity applications": [],
}
TAG_OVERRIDES = {  # judgment pass (no LLM)
    "Awardco": ["Future of Work"], "Benchmark Mineral Intelligence": ["Data & Analytics", "Climate / Sustainability"],
    "Business Monitor": ["Data & Analytics"], "EagleView": ["Data & Analytics", "FinTech / Insurance"],
    "Ease": ["Future of Work", "FinTech / Insurance"], "Employee Navigator": ["Future of Work", "FinTech / Insurance"],
    "Finalsite": ["Consumer"], "Goldbelly": ["Consumer", "CPG"], "GoodRx": ["Health", "Consumer"],
    "ITA Software": ["Transportation / Mobility"], "Jagex": ["Gaming / Media / Entertainment"],
    "OffSec": ["Cybersecurity", "Future of Work"], "Otter.ai": ["Future of Work"], "Prezi": ["Future of Work"],
    "Quavo": ["FinTech / Insurance", "Cybersecurity"], "RapidRatings": ["FinTech / Insurance", "Data & Analytics"],
    "RiskMetrics Group": ["FinTech / Insurance", "Data & Analytics"], "Tenstreet": ["Logistics / Supply Chain", "Future of Work"],
    "WorkFlex": ["Future of Work", "RegTech/Gov/Legal"], "Xapien": ["RegTech/Gov/Legal", "Data & Analytics"],
    "Zenwork": ["FinTech / Insurance", "RegTech/Gov/Legal"],
}
_WRAP = ("ShallowReactive", "Reactive", "Ref", "ShallowRef")


def devalue(arr):
    """Resolve a Nuxt `devalue` payload (flat array of index references)."""
    def r(i):
        v = arr[i]
        if isinstance(v, dict):
            return {k: r(x) if isinstance(x, int) else x for k, x in v.items()}
        if isinstance(v, list):
            if v and isinstance(v[0], str) and v[0] in _WRAP:
                return r(v[1])
            return [r(x) if isinstance(x, int) else x for x in v]
        return v
    return r(0)


def gql(payload):
    data = devalue(payload)["data"]
    return next(iter(data.values()))


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    landing = gql(fetch(BASE + "_payload.json", as_json=True))
    comps = landing["companies"]
    urls = [BASE + c["slug"] + "/_payload.json" for c in comps]
    pages = fetch_many(urls, workers=5, pause=0.15)
    out, seen = [], set()
    for c, u in zip(comps, urls):
        name = clean(c.get("name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        det = {}
        if pages.get(u):
            try:
                det = gql(json.loads(pages[u])).get("company") or {}
            except (ValueError, KeyError, IndexError, StopIteration):
                det = {}
        headline = clean(re.sub(r"\*", "", c.get("headline") or det.get("headline") or "")) or None
        status = clean(c.get("status") or det.get("status"))
        exit_s = clean(c.get("exitScenario") or det.get("exitScenario"))
        w = det.get("website")
        site = clean(w.get("ctaLink") if isinstance(w, dict) else w)
        if site and not site.startswith("http"):
            site = "https://" + site
        py = det.get("partnershipYear")
        ceo = det.get("ceo")
        out.append({
            "company_name": name,
            "description": headline,
            "company_url": clean_url(site) if site else None,
            "sectors": [s["name"] for s in c.get("sectors") or [] if s.get("name")],
            "themes": [s["name"] for s in c.get("themes") or [] if s.get("name")],
            "regions": [s["name"] for s in c.get("regions") or [] if s.get("name")],
            "location": clean(det.get("headquarters")),
            "first_invested": int(py) if py and str(py).isdigit() else None,
            "ceo": clean(ceo if isinstance(ceo, str) else None),
            "site_status": status,
            "status": "active" if (status or "").lower() == "current" else
                      ("acquired" if re.search(r"(?i)acquir|sold|merg", exit_s or "") else None),
            "exit_detail": exit_s,
            "profile_url": BASE + c["slug"] + "/",
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"], r["sectors"], SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "location", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
