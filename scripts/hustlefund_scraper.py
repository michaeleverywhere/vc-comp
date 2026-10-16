#!/usr/bin/env python3
"""
Hustle Fund portfolio scraper -> hustlefund_companies.json

Source: https://www.hustlefund.vc/founders ("Meet the Portfolio").

2026-10-16 rebuild: the site was re-platformed (Webflow + Finsweet CMS -> an
Astro/ploy build). The old `.founder-list-wrapper` CMS list and its
`?5d649f4d_page=N` pagination are gone; the "THE FULL ROSTER" panel on
/founders is now an iframe embedding Hustle Fund's own public Airtable shared
view (title "Hustle Fund portfolio directory"):

    https://airtable.com/embed/appjgQzUSfuMCb5pO/shrL7YrMPwpeky9ck

That shared view IS the firm's published portfolio directory -- the same data a
visitor scrolls on hustlefund.vc -- so it is read directly (not a third-party
source). The scraper first loads /founders and pulls the iframe src off the
page (so a re-pointed embed is followed automatically), then loads the embed
page, extracts the `readSharedViewData` URL + page-load id that the embed's own
JS uses, and requests that JSON (one call, all rows; no auth, no PAT).

Hustle Fund's own note on the page: "we only list founders from previous funds
that are fully deployed. We'll share more family members once we're done
deploying the current fund." -- so the list is the fully-deployed funds only.

Columns in the view (view "View - ALL PORTCOS for FOUNDER PAGE"):
  - Portco Name          -> company_name (verbatim; ~120 names are pipe-joined
                            "A | B" entity/rename strings and a few carry an
                            "(IVS)" suffix -- kept exactly as published;
                            `name_variants` holds the pipe-split parts)
  - Company Description  -> description (NEW: the old Webflow cards had none)
  - Industry - Master    -> sectors (multi-select, Hustle Fund's own taxonomy)
  - Geography - Category -> location (e.g. "US - Bay Area", "Asia - Singapore");
                            region = the coarse prefix (US / Asia / Africa /
                            Europe / Canada / Australia / Latin America /
                            Middle East / Remote) to stay comparable with the
                            pre-2026-10 region buckets
  - Company URL          -> company_url

Not published anywhere on the site: founders, founded year, funding stage,
first-invested date, financing, valuation, team size, exit/status. Fund I/II
membership was on the old cards but is no longer shown; post-processing
carries it (and nothing invented) from the previous dataset for matched rows.

requirements:
    pip install requests beautifulsoup4

usage:
    python3 hustlefund_scraper.py              # -> ../data/hustlefund_companies.json
    python3 hustlefund_scraper.py --limit 20   # quick test run
"""

import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

HOST = "www.hustlefund.vc"
FOUNDERS_URL = f"https://{HOST}/founders"
SOURCE_URL = FOUNDERS_URL
DEFAULT_EMBED = "https://airtable.com/embed/appjgQzUSfuMCb5pO/shrL7YrMPwpeky9ck"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                   "data", "hustlefund_companies.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 45
RETRIES = 3

# ---- Hustle Fund "Industry - Master" -> the 17-tag everywhere_tags set ------
# Deliberately unmapped (left to the keyword classifier over the description):
# "Artificial intelligence and machine learning (AI/ML)" (AI alone is not a
# category), "Software as a service (SaaS)", "Manufacturing", "Industrials",
# "Infrastructure", "Oil and gas", "Other".
SECTOR_TAG_MAP = {
    "Foodtech": ["CPG"],
    "Restaurant tech": ["Consumer"],
    "Agtech": ["Climate / Sustainability"],
    "Cloudtech and DevOps": ["Dev Tools / Cloud"],
    "Digital health": ["Health"],
    "Healthtech": ["Health"],
    "Lifestyles of Health and Sustainability (LOHAS) and wellness": ["Health"],
    "Life sciences": ["BioTech"],
    "Fintech": ["FinTech / Insurance"],
    "Insurtech": ["FinTech / Insurance"],
    "B2B payments": ["FinTech / Insurance"],
    "Sales / Operations / Customer Service": ["Future of Work"],
    "Future of Work": ["Future of Work"],
    "HR tech": ["Future of Work"],
    "Robotics and drones": ["Deeptech / Robotics / AR/VR"],
    "Hardware": ["Deeptech / Robotics / AR/VR"],
    "Space tech": ["Deeptech / Robotics / AR/VR"],
    "Virtual reality (VR)": ["Deeptech / Robotics / AR/VR"],
    "Augmented reality (AR)": ["Deeptech / Robotics / AR/VR"],
    "Adtech": ["Gaming / Media / Entertainment"],       # adtech sits in media
    "Marketing tech": ["Gaming / Media / Entertainment"],
    "Gaming and eSports": ["Gaming / Media / Entertainment"],
    "Audiotech": ["Gaming / Media / Entertainment"],
    "Social Media / Community / Networking": ["Gaming / Media / Entertainment", "Consumer"],
    "Legal tech": ["RegTech/Gov/Legal"],
    "Cryptocurrency and blockchain": ["Web3 / Crypto"],
    "Real estate tech": ["PropTech"],
    "Construction technology": ["PropTech"],
    "Cleantech and Climate tech": ["Climate / Sustainability"],
    "Supply chain and logistics": ["Logistics / Supply Chain"],
    "Cybersecurity": ["Cybersecurity"],
    "Ecommerce": ["Consumer"],
    "Edtech": ["Consumer"],
    "Pet tech": ["Consumer"],
    "Travel and hospitality": ["Consumer"],
    "Beauty / Fashion": ["CPG"],
    "Mobility tech": ["Transportation / Mobility"],
    "Carsharing": ["Transportation / Mobility"],
    "Big Data": ["Data & Analytics"],
}

# everywhere_tags keyword classifier (substrings, lowercased) -- copied verbatim
# from afore_scraper.py / iconiq_scraper.py so tagging stays consistent repo-wide.
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
                                     "wireless internet", "vertically integrated home"]),
    ("Consumer", ["marketplace", "consumer", "shopping", "social network", "community", "app for", "app that",
                  "ecommerce", "e-commerce", "subscription", "retailer", "universit", "student", "education",
                  "learning", "fashion", "parents", "creators", "fitness", "gig economy", "discounts", "tutor"]),
]


SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def get(url, **kw):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = SESSION.get(url, timeout=TIMEOUT, **kw)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            last = e
            print(f"  ! fetch failed {url[:90]} ({e}); retry {attempt}/{RETRIES}", file=sys.stderr)
            time.sleep(1.5 * attempt)
    raise SystemExit(f"FATAL: could not fetch {url}: {last}")


def clean(s):
    if s is None:
        return None
    s = re.sub(r"\s+", " ", str(s).replace("\xa0", " ")).strip()
    return s or None


def norm_url(u):
    u = clean(u)
    if not u or u == "#":
        return None
    if not re.match(r"https?://", u, re.I):
        u = "https://" + u.lstrip("/")
    parts = urlsplit(u)
    q = "&".join(p for p in parts.query.split("&")
                 if p and not re.match(r"(ref|utm_[a-z]+)=", p, re.I))
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, q, ""))


def find_embed_url():
    """The Airtable iframe on /founders; fall back to the known share if the
    page markup moves (logged so a change is visible)."""
    html = get(FOUNDERS_URL).text
    soup = BeautifulSoup(html, "html.parser")
    for ifr in soup.find_all("iframe"):
        src = ifr.get("src") or ""
        if "airtable.com/embed/" in src:
            return src
    print("  ! no airtable iframe on /founders -- using DEFAULT_EMBED", file=sys.stderr)
    return DEFAULT_EMBED


def read_shared_view(embed_url):
    m = re.search(r"/embed/(app\w+)/(shr\w+)", embed_url)
    if not m:
        raise SystemExit(f"FATAL: unexpected embed url {embed_url}")
    app_id = m.group(1)
    page = get(embed_url).text
    mu = re.search(r'urlWithParams:\s*"([^"]+)"', page)
    mp = re.search(r'"x-airtable-page-load-id":"(\w+)"', page)
    if not mu:
        raise SystemExit("FATAL: readSharedViewData url not found on embed page")
    path = json.loads('"' + mu.group(1) + '"')  # undo \u002F escaping
    headers = {
        "x-airtable-application-id": app_id,
        "x-airtable-inter-service-client": "webClient",
        "x-requested-with": "XMLHttpRequest",
        "x-time-zone": "America/New_York",
        "x-user-locale": "en",
        "accept": "application/json",
    }
    if mp:
        headers["x-airtable-page-load-id"] = mp.group(1)
    data = get("https://airtable.com" + path, headers=headers).json()
    return data["data"]["table"]


def region_of(location):
    if not location:
        return None
    head = location.split(" - ")[0].strip()
    return {"LatAm": "Latin America"}.get(head, head)


def everywhere_tags(name, description, sectors):
    """Hustle Fund's own industries first (SECTOR_TAG_MAP), then the shared
    keyword classifier over name + description + industry labels. Cap 4."""
    tags = []
    for sec in sectors:
        for mapped in SECTOR_TAG_MAP.get(sec, []):
            if mapped not in tags:
                tags.append(mapped)
    text = f" {name or ''} {description or ''} {' '.join(sectors)} ".lower()
    text = text.replace("machine learning", "ai").replace("deep learning", "ai")
    for tag, kws in KEYWORD_TAGS:
        if tag in tags:
            continue
        if any(kw in text for kw in kws):
            tags.append(tag)
    return tags[:4]


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    embed = find_embed_url()
    print(f"  embed: {embed}", file=sys.stderr)
    table = read_shared_view(embed)

    cols = {c["name"]: c for c in table["columns"]}
    def cid(name):
        c = cols.get(name)
        if not c:
            raise SystemExit(f"FATAL: column {name!r} missing; have {list(cols)}")
        return c["id"]
    C_NAME, C_DESC = cid("Portco Name"), cid("Company Description")
    C_IND, C_GEO, C_URL = cid("Industry - Master"), cid("Geography - Category"), cid("Company URL")
    ind_choices = {k: v["name"] for k, v in (cols["Industry - Master"].get("typeOptions") or {}).get("choices", {}).items()}
    geo_choices = {k: v["name"] for k, v in (cols["Geography - Category"].get("typeOptions") or {}).get("choices", {}).items()}

    rows = {r["id"]: r for r in table["rows"]}
    order = []
    for v in table.get("views") or []:
        for ro in v.get("rowOrder") or []:
            if ro.get("visibility", True) and ro["rowId"] in rows:
                order.append(ro["rowId"])
        break
    order += [rid for rid in rows if rid not in set(order)]

    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for rid in order:
        c = rows[rid].get("cellValuesByColumnId") or {}
        name = clean(c.get(C_NAME))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(c.get(C_DESC))
        sectors = [ind_choices.get(x, x) for x in (c.get(C_IND) or [])]
        geo = c.get(C_GEO)
        location = clean(geo_choices.get(geo, geo)) if geo else None
        variants = [p for p in (clean(x) for x in name.split("|")) if p]
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": norm_url(c.get(C_URL)),
            "region": region_of(location),
            "location": location,
            "sectors": sectors,
            "everywhere_tags": everywhere_tags(name, desc, sectors),
            "source_url": SOURCE_URL,
            "source_note": "Hustle Fund portfolio directory (Airtable embed on hustlefund.vc/founders); previous, fully deployed funds only",
            "scraped_at": scraped_at,
        }
        if len(variants) > 1:
            rec["name_variants"] = variants
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for f in ("description", "company_url", "region", "location", "sectors", "everywhere_tags"):
        print(f"  {f}: {sum(1 for r in out if r.get(f))}/{n} present")
    print("  regions:", dict(Counter(r["region"] for r in out)))
    tc = Counter(t for r in out for t in r["everywhere_tags"])
    print("  by everywhere_tag:", dict(tc.most_common()))


if __name__ == "__main__":
    main()
