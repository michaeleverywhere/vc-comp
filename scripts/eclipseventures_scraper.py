#!/usr/bin/env python3
"""
Eclipse Ventures portfolio scraper -> eclipseventures_companies.json

Scrapes Eclipse Ventures' public portfolio (https://eclipse.capital/companies)
into a JSON file. The site is Next.js + a headless **Sanity.io** CMS (project id
`5uq66tk5`, dataset `production`). The full company list is *not* reliably
server-rendered in the static HTML (the /companies page only embeds a teaser
subset); Sanity's public query API is reachable directly and unauthenticated:

    GET https://5uq66tk5.api.sanity.io/v2021-10-21/data/query/production
        ?query=<GROQ>

This returns every `_type=="company"` document (~53 as of this run) in one call,
with `companyCategory` and `teamMember` references resolved inline via a single
GROQ projection.

Schema notes:
  - `description`: portable-text `excerpt` preferred; falls back to `content`,
    then `lead`. Never fabricates prose.
  - `company_url`: `websiteURL` (53/53 present at build time).
  - `company_profile_url`: `https://eclipse.capital/companies/<slug>` when slug
    is present.
  - `logo_url`: `logo.asset->url` (cdn.sanity.io — not the unreachable
    cdn.webflow.com host).
  - `sectors`: Eclipse's own `companyCategory` names (Healthcare, Advanced
    Compute, Transportation & Mobility, ...). Category docs use `name` (not
    `title`) — verified live. "Uncategorized" is ignored if ever attached.
  - `stage`: Eclipse's own `companyStatus` multi-value list, mapped honestly to
    display labels Early Stage / Growth Stage (raw values: early_stage,
    growth_stage). No Acquired/Public/exit fields are published — checked names
    + descriptions for denormalized exit state (Empty != absent); none found,
    so status/acquirer/ticker are intentionally omitted, not invented.
  - `year_founded`: `foundedYear` (int → string), present for all 53 at build.
  - `location`: sparse (~7/53); emitted when present.
  - `founders`: free-text `founders` field when present (~3/53); else the
    free-text `team` field when it holds founder names (~32/53). Normalized to
    a list of name strings. The card `members` field is leadership/CEO display
    (often ≠ founders, e.g. Tenstorrent) and is NOT used as founders.
  - `partners`: Eclipse investment-team members resolved from `partners[]->`
    (`teamMember.name`).
  - No LinkedIn/Twitter fields exist on the company schema — `social_urls`
    omitted rather than emitted always-empty.
  - ARR / valuation / total raised / team size / last financing: not published;
    never invented.

requirements:
    pip install requests

usage:
    python3 eclipseventures_scraper.py            # writes ../data/eclipseventures_companies.json
    python3 eclipseventures_scraper.py --limit 10 # only the first ~10 for a test run
"""

import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone

import requests

SANITY_PROJECT = "5uq66tk5"
SANITY_DATASET = "production"
API = f"https://{SANITY_PROJECT}.api.sanity.io/v2021-10-21/data/query/{SANITY_DATASET}"
SOURCE_URL = "https://eclipse.capital/companies"
PROFILE_URL_TMPL = "https://eclipse.capital/companies/{slug}"
OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.pardir,
    "data",
    "eclipseventures_companies.json",
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 45
RETRIES = 3

# Category docs use `name` (not `title`); partners are teamMember refs.
GROQ_QUERY = """
*[_type=="company"]{
  title,
  "slug": slug.current,
  websiteURL,
  excerpt,
  content,
  lead,
  location,
  foundedYear,
  founders,
  team,
  companyStatus,
  "logo_url": logo.asset->url,
  "categories": categories[]->name,
  "partners": partners[]->{name, "slug": slug.current}
}
"""

# Eclipse companyCategory names -> the 17-tag everywhere_tags taxonomy.
# Only unambiguous verticals are mapped. "Advanced Compute" maps to Deeptech
# (chips / AI hardware / compute platforms — Eclipse's typical use); bare AI
# is not a category. "Defense & Security" is left to the keyword classifier
# (defense tech ≠ Cybersecurity; mapping it would systematically mis-tag).
# "Uncategorized" is ignored.
SECTOR_TAG_MAP = {
    "Healthcare": ["Health"],
    "Energy & Electrification": ["Climate / Sustainability"],
    "Industrial": ["Deeptech / Robotics / AR/VR"],
    "Construction & Real Estate": ["PropTech"],
    "Advanced Compute": ["Deeptech / Robotics / AR/VR"],
    "Climate Technology": ["Climate / Sustainability"],
    "Consumer": ["Consumer"],
    "Logistics & Supply Chain": ["Logistics / Supply Chain"],
    "Data Insights & Platforms": ["Data & Analytics"],
    "Workforce": ["Future of Work"],
    "Transportation & Mobility": ["Transportation / Mobility"],
    "Manufacturing": ["Deeptech / Robotics / AR/VR"],
    "Insurance": ["FinTech / Insurance"],
}

STAGE_DISPLAY = {
    "early_stage": "Early Stage",
    "growth_stage": "Growth Stage",
}

# everywhere_tags keyword classifier (substrings, lowercased) -- copied from
# afore_scraper.py / menlo_scraper.py so tagging stays consistent repo-wide.
KEYWORD_TAGS = [
    ("BioTech", ["biotech", "drug", "therapeut", "oncolog", "cancer", "tumor", "genomic", "genome",
                 "molecul", "antibod", "protein", "vaccine", "clinical-stage", "medicine", "opioid", "life science",
                 "synthetic biology", "biolog", "biomedical"]),
    ("Health", ["healthcare", "health care", "patient", "clinic", "medical", "mental health", "telehealth",
                "health system", "health record", "diagnos", "surgical", "doctor", "hospital", "pharmac", "therapy",
                "health plan", "prior authorization", "health assistant", "health data"]),
    ("Cybersecurity", ["cybersecurity", "security", "secure", "privacy", "fraud", "phishing", "malware",
                       "ransomware", "endpoint", "zero trust", "vulnerab", "authentication", "threat", "defense system", "identity",
                       "information protection", "kyb", "compliance for ai"]),
    ("FinTech / Insurance", ["fintech", "payment", "bank", "lending", "loan", "insurance", "insurtech", "credit", "trading",
                             "wallet", "financ", "invoic", "accounting", "payroll", "treasury", "billing", "pricing platform",
                             "rebate", " tax", "audit", "money management", "robo-advisor", "brokerage", "spend management",
                             "capital markets", "investing", "claims", "coverage plans", "underwriting"]),
    ("Web3 / Crypto", ["crypto", "blockchain", "web3", "token", "on-chain", "ethereum", "bitcoin", "decentral", "stablecoin", "nft"]),
    ("Gaming / Media / Entertainment", ["game", "gaming", "music", "video", "creator", "content", "publish",
                                        "entertain", "newsletter", "podcast", "film", "streaming", "social media", "media platform",
                                        "sports network", "filmmaker", "motion graphics", "audio file"]),
    ("Dev Tools / Cloud", ["developer", " api ", "apis", "api platform", "infrastructure", "database", "cloud",
                           "open source", "devops", "sdk", "kubernetes", "container", "observability", "deploy", "compute",
                           "storage", "serverless", "inference", "networking", "ethernet", "coding", "codebase", "low-code",
                           "no-code", "source code", "development platform", "incident", " sre", "voicemail", "communications",
                           "llm", "foundation model", "interpretability", "code-automation", "event-driven",
                           "log management", "file sharing", "tech stack", "voice agent", "appliance software",
                           "text to speech", "operationalize ai", "notifications for engineering",
                           "spreadsheet", "data importer"]),
    ("Data & Analytics", ["analytics", "business intelligence", "data platform", "data warehouse", "data lake",
                          "data pipeline", "insights", "dashboard", "experimentation", "decision intelligence", "data quality",
                          "analyz", "data curation", "quality management", "relationship intelligence",
                          "data discovery", "data analysis", "edge-data", "complex data", "real-world data", "analyst",
                          "data intelligence", "data transformation", "data integration", "data management", "buyer intent",
                          "curated coding data"]),
    ("Future of Work", ["workforce", "hiring", "recruit", "employee", "productivity", "collaborat", "talent",
                        "workplace", "human resources", " hr ", "learning platform", "customer success", "customer service",
                        "customer support", "presales", " sales ", "onboarding", "workflow", "saas management", "ai assistant",
                        "project management", "partnerships platform", "partnership", "teamwork", "scheduling", "work assistant",
                        "sales engineer", "sales teams", "for managers", "team wiki", "cleaning companies", "call center",
                        "answering service", "coaching", "well-being benefits", "presentation", "email", "inbox", "your notes"]),
    ("Transportation / Mobility", ["mobility", "vehicle", "transport", "autonomous", "fleet", "driving", "aviation",
                                   "aircraft", "electric vehicle", "scooter", " bike", "boat", "watercraft", "rideshar", "travel",
                                   "automotive"]),
    ("Logistics / Supply Chain", ["logistics", "supply chain", "supply and demand", "freight", "warehouse",
                                  "delivery", "procurement", "inventory", "fulfillment", "shipping", "container trucking",
                                  "last-mile", "distribution", "global supply"]),
    ("PropTech", ["real estate", "property", "housing", "mortgage", "rental", "construction", "tenant", "home construction",
                  "renovation", "rent"]),
    ("CPG", ["beverage", "snack", "consumer packaged", "beauty", "cosmetic", "apparel", "grocery", "skincare",
             "eyewear", "glasses", "footwear", "pet sitter", "pet ", "fashion brand", "secondhand"]),
    ("Climate / Sustainability", ["climate", "carbon", "renewable", "solar", "battery", "sustainab", "emission",
                                  "clean energy", "ev charging", "electrif", "energy", "power is produced", "power grid"]),
    ("RegTech/Gov/Legal", ["legal", "compliance", "government", "regulat", "law firm", "attorney", "risk services",
                           "lawsuit", "lawyer", "legal space", "ip protection", "prior authorization"]),
    ("Deeptech / Robotics / AR/VR", ["robot", "hardware", "semiconductor", "chip", "drone", "aerospace",
                                     "augmented reality", "virtual reality", "satellite", "quantum", "sensor", "rfid", "wifi",
                                     "space", "rocket", "launch vehicle", "optics", "defense", "warehouse automation",
                                     "wireless internet", "vertically integrated home", "manufactur", "industrial"]),
    ("Consumer", ["marketplace", "consumer", "shopping", "social network", "community", "app for", "app that",
                  "ecommerce", "e-commerce", "subscription", "retailer", "universit", "student", "education",
                  "learning", "fashion", "parents", "creators", "fitness", "gig economy", "discounts", "tutor"]),
]


def get_json(url, params=None):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last = e
            wait = 1.5 * attempt
            print(f"  ! request failed ({e}); retry {attempt}/{RETRIES} in {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
    raise SystemExit(f"FATAL: could not fetch {url}: {last}")


def clean(s):
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)
    s = re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()
    return s or None


def portable_text_to_plain(blocks):
    """Join span texts from Sanity portable-text block children into one string."""
    if not blocks:
        return None
    if isinstance(blocks, str):
        return clean(blocks)
    if not isinstance(blocks, list):
        return None
    parts = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        if block.get("_type") and block.get("_type") != "block":
            continue
        texts = []
        for child in block.get("children") or []:
            if isinstance(child, dict) and child.get("text"):
                texts.append(child["text"])
        para = "".join(texts).strip()
        if para:
            parts.append(para)
    return clean(" ".join(parts)) if parts else None


def split_names(s):
    """Normalize a free-text name list ('A, B & C' / 'A and B') to [str, ...]."""
    s = clean(s)
    if not s:
        return []
    parts = re.split(r"\s*(?:,|&|\band\b)\s*", s, flags=re.I)
    out = []
    for p in parts:
        p = clean(p)
        if p and p not in out:
            out.append(p)
    return out


def everywhere_tags(name, description, sectors):
    """Eclipse categories first (SECTOR_TAG_MAP), then keyword fallback on
    name + description. Order most->least relevant, cap at 4, no dups."""
    tags = []
    for sec in sectors or []:
        for mapped in SECTOR_TAG_MAP.get(sec, []):
            if mapped not in tags:
                tags.append(mapped)
    text = f"{name or ''} {description or ''}".lower()
    # substring-trap guard (see PLAYBOOK): "machine/deep learning" must NOT trip
    # the education "learning"/"learning platform" keywords -> neutralize to "ai".
    text = text.replace("machine learning", "ai").replace("deep learning", "ai")
    for tag, kws in KEYWORD_TAGS:
        if tag in tags:
            continue
        if any(kw in text for kw in kws):
            tags.append(tag)
    return tags[:4]


def fetch_all():
    data = get_json(API, params={"query": GROQ_QUERY})
    if "error" in data:
        raise SystemExit(f"FATAL: Sanity query error: {data['error']}")
    return data.get("result") or []


def build_record(c, scraped_at):
    name = clean(c.get("title"))
    if not name:
        return None

    description = (
        portable_text_to_plain(c.get("excerpt"))
        or portable_text_to_plain(c.get("content"))
        or portable_text_to_plain(c.get("lead"))
    )

    sectors = []
    for cat in c.get("categories") or []:
        cat = clean(cat)
        if cat and cat != "Uncategorized" and cat not in sectors:
            sectors.append(cat)

    stage = []
    for raw in c.get("companyStatus") or []:
        label = STAGE_DISPLAY.get(raw) or clean(raw)
        if label and label not in stage:
            stage.append(label)

    founders = split_names(c.get("founders"))
    if not founders:
        founders = split_names(c.get("team"))

    partners = []
    for p in c.get("partners") or []:
        if not isinstance(p, dict):
            continue
        pname = clean(p.get("name"))
        if pname and pname not in partners:
            partners.append(pname)

    slug = clean(c.get("slug"))
    year = c.get("foundedYear")
    year_founded = str(int(year)) if isinstance(year, (int, float)) and year else clean(year)

    return {
        "company_name": name,
        "description": description,
        "company_url": clean(c.get("websiteURL")),
        "company_profile_url": PROFILE_URL_TMPL.format(slug=slug) if slug else None,
        "logo_url": clean(c.get("logo_url")),
        "location": clean(c.get("location")),
        "year_founded": year_founded,
        "founders": founders,
        "partners": partners,
        "sectors": sectors,
        "stage": stage,
        "everywhere_tags": everywhere_tags(name, description, sectors),
        "source_url": SOURCE_URL,
        "scraped_at": scraped_at,
    }


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    raw = fetch_all()
    if limit:
        raw = raw[:limit]

    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    seen = set()
    for c in raw:
        rec = build_record(c, scraped_at)
        if not rec:
            continue
        if rec["company_name"] in seen:
            continue
        seen.add(rec["company_name"])
        out.append(rec)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    # ---- summary ----
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in (
        "description", "company_url", "company_profile_url", "logo_url",
        "location", "year_founded",
    ):
        present = sum(1 for r in out if r.get(field))
        print(f"  {field}: {present}/{n} present")
    print(f"  sectors: {sum(1 for r in out if r['sectors'])}/{n} present")
    print(f"  stage: {sum(1 for r in out if r['stage'])}/{n} present")
    print(f"  founders: {sum(1 for r in out if r['founders'])}/{n} present")
    print(f"  partners: {sum(1 for r in out if r['partners'])}/{n} present")
    stage_c = Counter(s for r in out for s in r["stage"])
    print(f"  stage distribution: {dict(stage_c)}")
    sector_c = Counter(s for r in out for s in r["sectors"])
    print("  sector distribution:")
    for sec, cnt in sector_c.most_common():
        print(f"    {sec}: {cnt}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged ({len(untagged)} untagged)"
          + (f" -> {untagged}" if untagged else ""))
    tag_c = Counter(t for r in out for t in r["everywhere_tags"])
    for tag, cnt in tag_c.most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
