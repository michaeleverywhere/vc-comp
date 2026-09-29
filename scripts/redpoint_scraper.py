#!/usr/bin/env python3
"""
Redpoint Ventures portfolio scraper -> redpoint_companies.json

Source: Gatsby page-data JSON at
  https://www.redpoint.com/page-data/companies/page-data.json
backed by Sanity CMS (project 22xmfoma). The companies page embeds the full
portfolio (~234) via GraphQL at build time — no per-company crawl needed.

Schema (only fields Redpoint publishes):
  company_name, description, company_url, company_profile_url, logo_url,
  sectors, stage, first_investment_date, everywhere_tags, source_url, scraped_at

usage:
    python3 scripts/redpoint_scraper.py
    python3 scripts/redpoint_scraper.py --limit 10
"""
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone

import requests

PAGE_DATA = "https://www.redpoint.com/page-data/companies/page-data.json"
SOURCE_URL = "https://www.redpoint.com/companies/"
PROFILE_TMPL = "https://www.redpoint.com/companies/{slug}/"
SANITY_IMG = "https://cdn.sanity.io/images/22xmfoma/production/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "redpoint_companies.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 45
RETRIES = 3

# Redpoint sector titles -> everywhere_tags. AI / Application / Infrastructure
# left to keyword classifier (AI alone isn't a category; Application/Infrastructure
# span multiple of our tags).
SECTOR_TAG_MAP = {
    "Blockchain": ["Web3 / Crypto"],
    "Consumer": ["Consumer"],
    "Fintech": ["FinTech / Insurance"],
    "Hardware": ["Deeptech / Robotics / AR/VR"],
    "Healthcare": ["Health"],
    "Security": ["Cybersecurity"],
}

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
                             "capital markets", "investing", "claims", "coverage plans", "underwriting", "payday", "paycheck", "earned wage"]),
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
                          "curated coding data", "data warehousing"]),
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
             "eyewear", "glasses", "footwear", "pet sitter", "pet ", "fashion brand", "secondhand", "fashion resale", "resale platform"]),
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


def get_json(url):
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last = e
            time.sleep(1.5 * attempt)
    raise SystemExit(f"FATAL: could not fetch {url}: {last}")


def clean(s):
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)
    s = re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()
    return s or None


def portable_text_to_plain(blocks):
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
        texts = []
        for child in block.get("children") or []:
            if isinstance(child, dict) and child.get("text"):
                texts.append(child["text"])
        para = "".join(texts).strip()
        if para:
            parts.append(para)
    return clean(" ".join(parts)) if parts else None


def logo_url(logo):
    if not logo or not isinstance(logo, dict):
        return None
    asset = logo.get("asset") or {}
    if asset.get("url"):
        return clean(asset["url"])
    aid = asset.get("_id") or ""
    # Sanity image id: image-<hash>-<WxH>-<ext>
    m = re.match(r"image-([a-f0-9]+)-(\d+x\d+)-(\w+)", aid)
    if m:
        return f"{SANITY_IMG}{m.group(1)}-{m.group(2)}.{m.group(3)}"
    return None


def everywhere_tags(name, description, sectors):
    tags = []
    for sec in sectors or []:
        for mapped in SECTOR_TAG_MAP.get(sec, []):
            if mapped not in tags:
                tags.append(mapped)
    text = f"{name or ''} {description or ''}".lower()
    text = text.replace("machine learning", "ai").replace("deep learning", "ai")
    for tag, kws in KEYWORD_TAGS:
        if tag in tags:
            continue
        if any(kw in text for kw in kws):
            tags.append(tag)
    return tags[:4]


def build_record(node, scraped_at):
    name = clean(node.get("title"))
    if not name:
        return None
    description = portable_text_to_plain(node.get("_rawExcerpt"))
    sectors = []
    for s in node.get("sectors") or []:
        if isinstance(s, dict):
            t = clean(s.get("title"))
            if t and t not in sectors:
                sectors.append(t)
    stage = []
    for s in node.get("stage") or []:
        if isinstance(s, dict):
            t = clean(s.get("title"))
            if t and t not in stage:
                stage.append(t)
    slug = None
    sl = node.get("slug")
    if isinstance(sl, dict):
        slug = clean(sl.get("current"))
    elif isinstance(sl, str):
        slug = clean(sl)
    inv = clean(node.get("investmentDate"))
    return {
        "company_name": name,
        "description": description,
        "company_url": clean(node.get("link")),
        "company_profile_url": PROFILE_TMPL.format(slug=slug) if slug else None,
        "logo_url": logo_url(node.get("logoColor") or node.get("logo")),
        "sectors": sectors,
        "stage": stage,
        "first_investment_date": inv,
        "everywhere_tags": everywhere_tags(name, description, sectors),
        "source_url": SOURCE_URL,
        "scraped_at": scraped_at,
    }


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    data = get_json(PAGE_DATA)
    edges = (((data.get("result") or {}).get("data") or {}).get("companies") or {}).get("edges") or []
    if limit:
        edges = edges[:limit]
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for e in edges:
        rec = build_record(e.get("node") or {}, scraped_at)
        if not rec or rec["company_name"] in seen:
            continue
        seen.add(rec["company_name"])
        out.append(rec)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for field in ("description", "company_url", "company_profile_url", "logo_url", "first_investment_date"):
        print(f"  {field}: {sum(1 for r in out if r.get(field))}/{n}")
    print(f"  sectors: {sum(1 for r in out if r['sectors'])}/{n}")
    print(f"  stage: {sum(1 for r in out if r['stage'])}/{n}")
    untagged = [r["company_name"] for r in out if not r["everywhere_tags"]]
    print(f"  everywhere_tags: {n - len(untagged)}/{n} tagged ({len(untagged)} untagged)"
          + (f" -> {untagged[:20]}" if untagged else ""))
    tag_c = Counter(t for r in out for t in r["everywhere_tags"])
    for tag, cnt in tag_c.most_common():
        print(f"    {tag}: {cnt}")


if __name__ == "__main__":
    main()
