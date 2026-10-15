#!/usr/bin/env python3
"""
Sequoia Capital portfolio scraper -> sequoia_companies.json

Scrapes Sequoia's portfolio (https://www.sequoiacap.com/our-companies/) into a
JSON file. WordPress + FacetWP. The listing page renders a server-side HTML
<table> (one <tr> per company, class `company-listing__head` etc.) that is
paginated with a normal WP query var, `?_paged=N` (confirmed: 7 pages of 52 +
1 page of 48 = 412 total, alphabetical, no overlap/duplication across pages).

Each row gives: internal post id (`data-toggle="collapse" data-target=
"#company_listing-<id>"`), name, a short description, "Current Stage"
(Pre-Seed/Seed|Early|Growth|Acquired|IPO), an abbreviated partner list, and
"First Partnered" stage+year. The richer per-company data (website, logo,
socials, categories, founders, full partner list, founded/partnered/exit
years, "Why we Partnered") only loads on-demand via an admin-ajax POST
(`action=load_company_content&post_id=<id>&nonce=<nonce>`; the nonce is
embedded in the listing page as `window.vars.nonce` and appears reusable
across companies/pages within a scrape run) -- so this scraper does one
listing-page fetch per page plus one detail fetch per company (~412 + 8
requests).

Empty != absent, checked: Sequoia publishes NO ticker symbol anywhere (listing
descriptions, detail descriptions, or milestones -- grepped for NASDAQ/NYSE
across all 67 IPO'd companies' short + long descriptions: zero hits), so
`ticker_symbol` is left null for all records -- this is a genuine site-wide
omission, not denormalized data we missed. Acquirer IS denormalized in prose,
though only for some: the short/long description often says "now part of X",
"now a part of X", or "(acquired by X)" (confirmed on ~20/37 Acquired
companies on a sampled page; the rest, e.g. Armis, simply don't name a buyer
in the description) -- parsed via regex into `acquirer`. Exit year comes from
the structured Milestones list ("Acquired 2010" / "IPO 2020"), not the name
suffix (Sequoia doesn't suffix names like RRE does).

requirements:
    pip install requests beautifulsoup4

usage:
    python3 sequoia_scraper.py            # writes ../data/sequoia_companies.json
    python3 sequoia_scraper.py --limit 20 # only the first ~20 for a test run
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

BASE = "https://www.sequoiacap.com/our-companies/"
AJAX_URL = "https://sequoiacap.com/wp-admin/admin-ajax.php"
SOURCE_URL = "https://www.sequoiacap.com/our-companies/"
SEARCH_INDEX_URL = (
    "https://framerusercontent.com/sites/1b1QJ6Gr5B06KwaurpRpvu/"
    "searchIndex-AkDTj8w0wyx8.json"
)
SITE = "https://www.sequoiacap.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "sequoia_companies.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 45
RETRIES = 3
SLEEP = 0.5

# Sequoia's own 17 "categories" facet slugs -> display names (from
# window.FWP_JSON.preload_data.facets.categories on the listing page; also
# matches the pill text rendered in each company's detail HTML).
CATEGORY_SLUG_DISPLAY = {
    "ai": "AI",
    "climate": "Climate",
    "consumer": "Consumer",
    "crypto": "Crypto",
    "data-analytics": "Data & Analytics",
    "defense": "Defense",
    "developer-tools": "Developer Tools",
    "fintech": "Fintech",
    "gtm": "GTM",
    "hardware": "Hardware",
    "healthcare": "Healthcare",
    "infrastructure": "Infrastructure",
    "legal": "Legal",
    "marketplace": "Marketplace",
    "operations": "Operations",
    "productivity": "Productivity",
    "security": "Security",
}

# Sequoia categories -> the 17-tag everywhere_tags taxonomy. "AI" and "GTM" /
# "Operations" / "Productivity" are intentionally NOT mapped here: AI alone is
# not a category (classify by market served) and GTM/Operations/Productivity
# don't correspond to a single vertical tag -- left to the keyword fallback.
SECTOR_TAG_MAP = {
    "Climate": ["Climate / Sustainability"],
    "Crypto": ["Web3 / Crypto"],
    "Data & Analytics": ["Data & Analytics"],
    "Defense": ["Deeptech / Robotics / AR/VR"],
    "Developer Tools": ["Dev Tools / Cloud"],
    "Fintech": ["FinTech / Insurance"],
    "Hardware": ["Deeptech / Robotics / AR/VR"],
    "Healthcare": ["Health"],
    "Infrastructure": ["Dev Tools / Cloud"],
    "Legal": ["RegTech/Gov/Legal"],
    "Marketplace": ["Consumer"],
    "Consumer": ["Consumer"],
}

# everywhere_tags keyword classifier (substrings, lowercased) -- copied from
# rre_scraper.py / iconiq_scraper.py.
KEYWORD_TAGS = [
    ("BioTech", ["biotech", "drug", "therapeut", "oncolog", "cancer", "tumor", "genomic", "genome",
                 "molecul", "antibod", "protein", "vaccine", "clinical-stage", "medicine", "opioid", "life science",
                 "synthetic biology", "biolog"]),
    ("Health", ["healthcare", "health care", "patient", "clinic", "medical", "mental health", "telehealth",
                "health system", "health record", "diagnos", "surgical", "doctor", "hospital", "pharmac", "therapy"]),
    ("Cybersecurity", ["cybersecurity", "security", "secure", "privacy", "fraud", "phishing", "malware",
                       "ransomware", "endpoint", "zero trust", "vulnerab", "authentication", "threat", "defense system", "identity",
                       "information protection"]),
    ("FinTech / Insurance", ["fintech", "payment", "bank", "lending", "loan", "insurance", "credit", "trading",
                             "wallet", "financ", "invoic", "accounting", "payroll", "treasury", "billing", "pricing platform",
                             "rebate", " tax", "audit", "money management", "robo-advisor", "brokerage", "spend management",
                             "capital markets", "investing", "claims"]),
    ("Web3 / Crypto", ["crypto", "blockchain", "web3", "token", "on-chain", "ethereum", "bitcoin", "decentral", "stablecoin", "nft"]),
    ("Gaming / Media / Entertainment", ["game", "gaming", "music", "video", "creator", "content", "publish",
                                        "entertain", "newsletter", "podcast", "film", "streaming", "social media", "media platform"]),
    ("Dev Tools / Cloud", ["developer", " api ", "apis", "api platform", "infrastructure", "database", "cloud",
                           "open source", "devops", "sdk", "kubernetes", "container", "observability", "deploy", "compute",
                           "storage", "serverless", "inference", "networking", "ethernet", "coding", "codebase", "low-code",
                           "no-code", "source code", "development platform", "incident", " sre", "voicemail", "communications",
                           "llm", "foundation model", "interpretability", "voice keyboard", "voice recognition", "frame relay",
                           "log management", "file sharing", "tech stack", "voice agent", "appliance software",
                           "text to speech", "code"]),
    ("Data & Analytics", ["analytics", "business intelligence", "data platform", "data warehouse", "data lake",
                          "data pipeline", "insights", "dashboard", "experimentation", "decision intelligence", "data quality",
                          "analyz", "data curation", "quality management", "relationship intelligence",
                          "data discovery", "data analysis", "edge-data", "complex data", "real-world data", "analyst",
                          "data intelligence", "data transformation", "data integration"]),
    ("Future of Work", ["workforce", "hiring", "recruit", "employee", "productivity", "collaborat", "talent",
                        "workplace", "human resources", " hr ", "learning platform", "customer success", "customer service",
                        "customer support", "presales", " sales ", "onboarding", "workflow", "saas management", "ai assistant",
                        "project management", "partnerships platform", "partnership", "teamwork", "scheduling", "work assistant"]),
    ("Transportation / Mobility", ["mobility", "vehicle", "transport", "autonomous", "fleet", "driving", "aviation",
                                   "aircraft", "electric vehicle", "scooter", " bike", "boat", "watercraft", "rideshar", "travel"]),
    ("Logistics / Supply Chain", ["logistics", "supply chain", "supply and demand", "freight", "warehouse",
                                  "delivery", "procurement", "inventory", "fulfillment", "shipping"]),
    ("PropTech", ["real estate", "property", "housing", "mortgage", "rental", "construction", "tenant"]),
    ("CPG", ["beverage", "snack", "consumer packaged", "beauty", "cosmetic", "apparel", "grocery", "skincare",
             "eyewear", "glasses", "footwear", "pet sitter", "pet "]),
    ("Climate / Sustainability", ["climate", "carbon", "renewable", "solar", "battery", "sustainab", "emission",
                                  "clean energy", "ev charging", "electrif", "energy", "power is produced", "power grid"]),
    ("RegTech/Gov/Legal", ["legal", "compliance", "government", "regulat", "law firm", "attorney", "risk services",
                           "lawsuit", "lawyer"]),
    ("Deeptech / Robotics / AR/VR", ["robot", "hardware", "semiconductor", "chip", "drone", "aerospace",
                                     "augmented reality", "virtual reality", "satellite", "quantum", "sensor", "rfid", "wifi",
                                     "space", "rocket", "launch vehicle", "optics", "defense"]),
    ("Consumer", ["marketplace", "consumer", "shopping", "social network", "community", "app for", "app that",
                  "ecommerce", "e-commerce", "subscription", "retailer", "universit", "student", "education",
                  "learning", "fashion"]),
]



import gzip


def get_bytes(url):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            return r.content
        except requests.RequestException as e:  # noqa
            last = e
            wait = 1.5 * attempt
            print(f"  ! request failed ({e}); retry {attempt}/{RETRIES} in {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
    raise SystemExit(f"FATAL: could not fetch {url}: {last}")


def clean(s):
    if s is None:
        return None
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def to_year(s):
    s = clean(s)
    if s and re.fullmatch(r"\d{4}", s):
        y = int(s)
        if 1900 <= y <= 2100:
            return y
    return None


ACQUIRER_PATTERNS = [
    re.compile(r"now (?:a )?part of ([A-Z][A-Za-z0-9&.\- ]*?)(?:,| is | provides | builds | makes |\.|$)", re.I),
    re.compile(r"\(acquired by ([A-Z][A-Za-z0-9&.\- ]*?)\)", re.I),
    re.compile(r"acquired by ([A-Z][A-Za-z0-9&.\- ]*?)(?:,| in | for |\.|$)", re.I),
]


def derive_acquirer(text):
    if not text:
        return None
    for pat in ACQUIRER_PATTERNS:
        m = pat.search(text)
        if m:
            acquirer = clean(m.group(1))
            if acquirer:
                return acquirer.rstrip(", ")
    return None


def everywhere_tags(name, description, categories):
    tags = []
    for cat in categories:
        for mapped in SECTOR_TAG_MAP.get(cat, []):
            if mapped not in tags:
                tags.append(mapped)
    text = f"{name or ''} {description or ''}".lower()
    for tag, kws in KEYWORD_TAGS:
        if tag in tags:
            continue
        if any(kw in text for kw in kws):
            tags.append(tag)
    return tags[:4]


NAV_SKIP = {
    "our founders", "our companies", "our team", "stories", "podcasts", "arc",
    "about", "our ethos", "our history", "jobs", "legal", "business entities",
    "sequoia capital", "sequoia global equities", "login", "lp login",
    "sequoia ampersand login", "motion", "on", "off", "partners", "partner",
    "milestones", "team", "press & media", "why we partnered",
}


def looks_like_domain(s):
    s = (s or "").strip().lower()
    if not s or " " in s or s.startswith("http"):
        return False
    if s.count(".") < 1:
        return False
    # anthropic.com / n.xyz / 247.ai
    return bool(re.fullmatch(r"[a-z0-9][a-z0-9.-]+\.[a-z]{2,}(/)?", s.rstrip("/")))


def parse_company_entry(path, entry):
    """Turn one Framer searchIndex /companies/<slug> record into a portfolio row."""
    title = clean(entry.get("title") or "")
    name = title.split("|")[0].strip() if title else None
    if not name:
        return None
    ps = [clean(x) for x in (entry.get("p") or []) if clean(x)]
    meta_desc = clean(entry.get("description") or "")
    # Prefer the long company blurb in p[] over generic site meta
    blurb = None
    for p in ps:
        if p.lower() in NAV_SKIP:
            continue
        if looks_like_domain(p):
            continue
        if re.match(r"^(Founded|Partnered|Acquired|IPO)\s+\d{4}$", p, re.I):
            continue
        if p.startswith("©"):
            continue
        if len(p) >= 40:
            blurb = p
            break
    description = blurb or (meta_desc if meta_desc and "daring build legendary" not in meta_desc.lower() else None)

    company_url = None
    founded_year = partnered_year = exit_year = None
    status = "active"
    founders = []
    partners = []
    mode = "founders"  # after domain/years, names are founders until "Partners"
    for p in ps:
        pl = p.lower()
        if pl in NAV_SKIP or p.startswith("©"):
            if pl == "partners":
                mode = "partners"
            continue
        if looks_like_domain(p):
            company_url = "https://" + p.rstrip("/")
            continue
        m = re.match(r"^Founded\s+(\d{4})$", p, re.I)
        if m:
            founded_year = to_year(m.group(1)); continue
        m = re.match(r"^Partnered\s+(\d{4})$", p, re.I)
        if m:
            partnered_year = to_year(m.group(1)); continue
        m = re.match(r"^Acquired\s+(\d{4})$", p, re.I)
        if m:
            status = "acquired"; exit_year = to_year(m.group(1)); continue
        m = re.match(r"^IPO\s+(\d{4})$", p, re.I)
        if m:
            status = "public"; exit_year = to_year(m.group(1)); continue
        # person names: Title Case, short, no URL-ish
        if re.fullmatch(r"[A-Z][A-Za-zÀ-ÿ'’.\-]+(?:\s+[A-Z][A-Za-zÀ-ÿ'’.\-]+){0,3}", p) and len(p) < 60:
            if mode == "partners":
                partners.append(p)
            else:
                # avoid treating milestones headers etc.
                if p not in founders and p not in partners:
                    founders.append(p)

    acquirer = derive_acquirer(description or "")
    categories = []  # Framer index does not expose Sequoia category chips
    rec = {
        "company_name": name,
        "description": description,
        "company_url": company_url,
        "logo_url": None,
        "social_urls": {},
        "categories": categories,
        "founders": founders or None,
        "sequoia_partners": partners or None,
        "why_we_partnered": None,
        "founded_year": founded_year,
        "first_partnered_year": partnered_year,
        "first_partnered_stage": None,
        "status": status,
        "acquirer": acquirer,
        "exit_year": exit_year,
        "ticker_symbol": None,
        "location": None,
        "everywhere_tags": everywhere_tags(name, description, categories),
        "source_url": SITE + path,
        "scraped_at": None,  # filled in main
    }
    return rec


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    print(f"Fetching Framer searchIndex: {SEARCH_INDEX_URL}")
    raw = get_bytes(SEARCH_INDEX_URL)
    try:
        data = gzip.decompress(raw)
    except OSError:
        data = raw
    index = json.loads(data)
    paths = sorted(k for k in index if isinstance(k, str) and k.startswith("/companies/"))
    print(f"  {len(paths)} company pages in index")
    if limit:
        paths = paths[:limit]
        print(f"  --limit {limit}")

    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for path in paths:
        rec = parse_company_entry(path, index[path])
        if not rec:
            continue
        rec["scraped_at"] = scraped_at
        out.append(rec)

    # stable sort by name
    out.sort(key=lambda r: (r.get("company_name") or "").lower())

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in ("description", "company_url", "founders", "founded_year", "first_partnered_year", "status"):
        miss = sum(1 for r in out if not r.get(field))
        print(f"  {field:22s} missing: {miss}/{n}")
    by_status = {}
    for r in out:
        by_status[r.get("status")] = by_status.get(r.get("status"), 0) + 1
    print(f"  status breakdown: {by_status}")
    untagged = sum(1 for r in out if not r.get("everywhere_tags"))
    print(f"  untagged: {untagged}/{n}")


if __name__ == "__main__":
    main()
