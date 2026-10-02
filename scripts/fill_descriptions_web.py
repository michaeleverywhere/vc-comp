#!/usr/bin/env python3
"""
Fill empty company descriptions from the open internet.

ALLOWED: company official websites (meta/about), Wikidata, other public non-paywalled pages.
FORBIDDEN: Crunchbase, LinkedIn, PitchBook; inventing copy; overwriting non-empty descriptions.

Rules:
  - Fill only empty description (and company_name if somehow empty).
  - Prefer short accurate blurbs from official site meta/about.
  - Reject parked domains and mis-attribution.
  - For schemas lacking a description key (e.g. coatue), introduce description only when
    a verified blurb is found (needed for all_companies / Private Comps).
  - Never invent; prefer empty over guessed copy.

Usage:
  python3 scripts/fill_descriptions_web.py
  python3 scripts/fill_descriptions_web.py --firms gv,coatue,boxgroup --limit 50
  python3 scripts/fill_descriptions_web.py --workers 24 --priority-only
"""
from __future__ import annotations

import argparse
import html as htmlmod
import json
import re
import sys
import time
import traceback
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "automation"))
import identity  # noqa: E402

UA = {
    "User-Agent": (
        "vc-comps-desc-fill/1.0 (+https://github.com/michaeleverywhere/vc-comp; "
        "research backfill of empty portfolio descriptions)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
WD_API = "https://www.wikidata.org/w/api.php"
# Per-call requests (Session is not thread-safe under ThreadPoolExecutor)

# High-gap firms from prior firm-site backfill (prioritize first)
PRIORITY = [
    # URL-rich first (site meta is fast + high yield)
    "coatue", "boxgroup", "hustlefund", "generalcatalyst", "norwest",
    "svangel", "m12", "entreecapital", "resoluteventures", "titaniumventures",
    "signalfire", "meritech", "capitalg", "whitestarcapital", "blockchaincapital",
    "greatoaksventurecapital", "a16z",
    # Low/no URL — Wikidata-only (slower, lower yield)
    "gv", "slowventures", "ribbit", "uncork", "earlybird", "reachcapital",
    "dragoneer",
]

# Wikidata instance-of QIDs that indicate a company/org (not a person/event)
ORG_P31 = {
    "Q4830453",   # business enterprise
    "Q783794",    # company
    "Q891723",    # public company
    "Q6881511",   # enterprise
    "Q167037",    # corporation
    "Q43229",     # organization
    "Q18388277",  # technology company
    "Q161718",    # software company
    "Q163740",    # nonprofit organization
    "Q15893266",  # former entity
    "Q783794",    # company
    "Q21980538",  # startup company
    "Q1668024",   # service company
    "Q475000",    # software company (alt)
    "Q2085381",   # publishing company
    "Q1797819",   # financial institution? skip vague
    "Q2659904",   # government organization — skip
    "Q22687",     # bank
    "Q131093",    # fashion house
    "Q110979095", # AI company
}
# Broader accept if description looks company-like even when P31 missing
COMPANYISH_DESC = re.compile(
    r"(?i)\b(company|startup|enterprise|business|platform|provider|"
    r"manufacturer|developer|firm|lab|laborator|biotech|fintech|"
    r"marketplace|network|service|software|hardware|venture)\b"
)
PERSON_P31 = {"Q5"}  # human

PARKED = re.compile(
    r"(?i)("
    r"domain\s+(is\s+)?for\s+sale|buy this domain|godaddy|parked\s+free|"
    r"sedoparking|hugedomains|this domain may be for sale|related searches|"
    r"domain parking|parkingcrew|above\.com|dan\.com\s+for\s+sale|"
    r"is expired|renew now|this webpage is parked|coming soon"
    r")"
)
JUNK_META = re.compile(
    r"(?i)^("
    r"home|welcome|just a moment|attention required|access denied|"
    r"403|404|cloudflare|loading\.?|subscribe|sign up|log[\s-]?in|"
    r"cookie|javascript required|enable javascript|page not found|"
    r"error|untitled|default|wordpress|squarespace|wix\.com|"
    r"shopify|webflow|v0|lovable|framer"
    r")\.?$"
)
FORBIDDEN_HOST = re.compile(
    r"(?i)(^|\.)("
    r"crunchbase\.com|linkedin\.com|pitchbook\.com|bloomberg\.com|"
    r"facebook\.com|twitter\.com|x\.com|instagram\.com|youtube\.com|"
    r"medium\.com|substack\.com|angel\.co|wellfound\.com|"
    r"tracxn\.com|cbinsights\.com|owler\.com|zoominfo\.com|"
    r"wikipedia\.org"  # use Wikidata API instead; avoid scraping wiki HTML
    r")$"
)
# Meta that is clearly the VC firm's own site, not the company
VC_SELF = re.compile(
    r"(?i)\b(venture capital|venture fund|investment fund|early.?stage "
    r"(investment|venture)|seed fund|growth equity fund)\b"
)


# Firm slug -> display name for name-only context searches
_FIRM_NAMES = {}
try:
    _fn = json.loads((ROOT / "automation" / "firm_names.json").read_text())
    for fname, dname in (_fn.get("names") or {}).items():
        slug = fname.replace("_companies.json", "").replace("companies.json", "lightspeed")
        _FIRM_NAMES[slug] = dname
except Exception:
    pass

CLEARBIT = "https://autocomplete.clearbit.com/v1/companies/suggest"
DDG_IA = "https://api.duckduckgo.com/"
PREFERRED_TLD = {
    "com", "io", "ai", "co", "so", "app", "dev", "tech", "net", "org", "us",
    "uk", "de", "fr", "ch", "ca", "au", "nl", "se", "fi", "no", "es", "it",
    "xyz", "gg", "me", "health", "care", "bio", "finance", "capital",
}
DOMAIN_SUFFIXES = {
    "", "hq", "app", "labs", "lab", "bio", "tx", "ai", "io", "inc", "co",
    "tech", "health", "care", "capital", "finance", "pay", "dev", "energy",
    "ventures", "vc", "get", "try", "use", "go", "team", "api", "hq",
}


def norm_alnum(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def sig_tokens(name: str) -> list[str]:
    raw = re.findall(r"[A-Za-z0-9][A-Za-z0-9+.-]*", name or "")
    stop = {
        "inc", "llc", "ltd", "gmbh", "ag", "corp", "co", "the", "and", "of",
        "company", "technologies", "therapeutics", "labs", "lab", "systems",
        "group", "ai", "biosciences", "therapeutics", "ventures",
    }
    return [t for t in raw if t.lower() not in stop]


def domain_aligned(name: str, domain: str) -> bool:
    """Require domain base to match company name tightly (blocks Alan→alanba, Amper→amperevehicles)."""
    n = norm_alnum(name)
    if not n or not domain:
        return False
    host = domain.lower()
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    base = parts[0]
    # strip common marketing prefixes
    # Only strip marketing prefixes that are unlikely to be part of the brand
    # (never strip "go"/"hi" — they mangle goodbill, gong, hive, etc.)
    for p in ("get", "try", "use", "ask", "join", "with"):
        if base.startswith(p) and len(base) > len(p) + 3:
            base = base[len(p):]
            break
    if base == n:
        return True
    for suf in DOMAIN_SUFFIXES:
        if base == n + suf:
            return True
    # multi-word collapsed: antoraenergy
    if n == base:
        return True
    # name starts with domain base (Affinia Therapeutics → affiniatx / affinia)
    if len(base) >= 4 and n.startswith(base):
        return True
    # domain base starts with full name + short suffix (accenttx)
    if len(n) >= 5 and base.startswith(n) and len(base) - len(n) <= 4:
        return True
    # any significant token (≥4) equals base or base startswith token + short suffix
    # (Bank Jago → jago.com; AMP Robotics → amprobotics)
    toks = sig_tokens(name)
    for tok in toks:
        t0 = norm_alnum(tok)
        if len(t0) < 4:
            continue
        if base == t0:
            return True
        for suf in DOMAIN_SUFFIXES:
            if base == t0 + suf:
                return True
        if base.startswith(t0) and len(base) - len(t0) <= 3:
            return True
    # short names (<5): only exact base match (already handled) — reject substring friends
    if len(n) < 5:
        return False
    return False



def tld_rank(domain: str) -> int:
    """Lower is better. Prefer global product TLDs over random ccTLDs."""
    host = domain.lower()
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    tld = parts[-1]
    if len(parts) >= 3 and parts[-2] in {"co", "com", "org", "net"}:
        # co.uk / com.au / co.za — treat as the compound
        compound = parts[-2] + "." + tld
        order = {
            "co.uk": 15, "com.au": 40, "co.za": 45, "co.nz": 20, "com.br": 40,
            "co.id": 25, "co.jp": 20, "com.mx": 30, "co.in": 30,
        }
        return order.get(compound, 35)
    order = {
        "com": 0, "io": 1, "ai": 2, "app": 3, "co": 4, "so": 5, "dev": 6,
        "tech": 7, "net": 8, "org": 9, "us": 10, "gg": 11, "me": 12,
        "health": 8, "care": 8, "bio": 8, "finance": 8, "capital": 12,
        "uk": 15, "de": 18, "fr": 18, "ch": 18, "ca": 16, "au": 40,
        "nl": 20, "se": 18, "fi": 18, "no": 18, "es": 20, "it": 20,
        "xyz": 25, "id": 25, "za": 45, "br": 40, "il": 35, "ru": 50,
        "cn": 50,
    }
    return order.get(tld, 60)


def tld_ok(domain: str) -> bool:
    host = domain.lower()
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if len(parts) < 2:
        return False
    tld = parts[-1]
    if tld in PREFERRED_TLD:
        return True
    # co.uk etc
    if len(parts) >= 3 and parts[-2] in {"co", "com", "org", "net"} and tld.isalpha():
        return True
    return False


def extract_title(html: str) -> str | None:
    m = re.search(r"<title[^>]*>(.*?)</title>", html or "", re.I | re.S)
    if not m:
        return None
    return clean_text(re.sub(r"<[^>]+>", "", m.group(1)))


def name_in_text(name: str, *texts: str | None) -> bool:
    """Require company name (or a significant token) as a word, not a substring
    (blocks Rocket⊂WebRocket)."""
    if not name:
        return False
    blob = " ".join(t or "" for t in texts).lower()
    if not blob:
        return False
    # Full name as phrase
    if name.strip().lower() in blob:
        return True
    n = norm_alnum(name)
    if len(n) >= 5 and n in norm_alnum(blob):
        return True
    for t in sig_tokens(name):
        if len(t) < 4:
            continue
        if re.search(rf"(?<![a-z0-9]){re.escape(t.lower())}(?![a-z0-9])", blob):
            return True
    return False


def clearbit_domain(name: str) -> tuple[str | None, str]:
    if not name or len(name.strip()) < 2:
        return None, "cb_no_name"
    if len(norm_alnum(name)) < 5:
        return None, "cb_short_name"
    try:
        r = requests.get(CLEARBIT, params={"query": name.strip()}, headers=UA, timeout=12)
    except requests.RequestException as e:
        return None, f"cb_err:{type(e).__name__}"
    if r.status_code >= 400:
        return None, f"cb_http_{r.status_code}"
    hits = r.json() or []
    if not hits:
        return None, "cb_empty"
    n = norm_alnum(name)
    # Prefer exact Clearbit name matches with aligned preferred-TLD domains
    exact = [h for h in hits if norm_alnum(h.get("name") or "") == n]
    # Exact Clearbit name matches ONLY; prefer strong TLDs (.com/.io/.ai over .co.za)
    if not exact:
        return None, "cb_no_exact"
    candidates = []
    for h in exact:
        dom = (h.get("domain") or "").lower().strip()
        if not dom or FORBIDDEN_HOST.search(dom):
            continue
        if not tld_ok(dom):
            continue
        if not domain_aligned(name, dom):
            continue
        candidates.append(dom)
    if not candidates:
        return None, "cb_no_aligned"
    candidates.sort(key=tld_rank)
    best = candidates[0]
    # Single-token short names on weak ccTLDs only → too uncertain
    if tld_rank(best) >= 40 and len(n) < 8 and len(sig_tokens(name)) <= 1:
        return None, "cb_weak_tld_uncertain"
    return best, "clearbit"


def ddg_ia_blurb(name: str, firm_name: str | None) -> tuple[str | None, str]:
    """DuckDuckGo Instant Answer (usually Wikipedia abstract).

    Short/ambiguous names are skipped (leave empty if uncertain). Firm display
    name is folded into the query as weak context; abstract must still look like
    a company and be name-grounded.
    """
    n = norm_alnum(name or "")
    # Short names are too ambiguous (Alan→bike brand, Amper→river)
    if not name or len(n) < 6:
        return None, "ddg_short_name"
    # Prefer "Name company" / "Name firm" to bias toward orgs
    queries = [name.strip()]
    if firm_name:
        queries.insert(0, f'{name.strip()} {firm_name}')
    queries.append(f"{name.strip()} company")

    best_reject = "ddg_no_abstract"
    for q in queries:
        try:
            r = requests.get(
                DDG_IA,
                params={"q": q, "format": "json", "no_html": 1, "skip_disambig": 1},
                headers=UA,
                timeout=15,
            )
        except requests.RequestException as e:
            best_reject = f"ddg_err:{type(e).__name__}"
            continue
        if r.status_code >= 400:
            best_reject = f"ddg_http_{r.status_code}"
            continue
        try:
            j = r.json()
        except ValueError:
            best_reject = "ddg_bad_json"
            continue
        abstract = (j.get("Abstract") or "").strip()
        heading = (j.get("Heading") or "").strip()
        abs_url = (j.get("AbstractURL") or "")
        if not abstract:
            best_reject = "ddg_no_abstract"
            continue
        if abs_url:
            host = domain_of(abs_url) or ""
            if FORBIDDEN_HOST.search(host) and "wikipedia.org" not in host:
                best_reject = "ddg_forbidden_src"
                continue
        if not name_in_text(name, abstract, heading):
            best_reject = "ddg_ungrounded"
            continue
        if re.search(
            r"(?i)\b(medal|award|decoration|video game|song|album|film\b|movie|"
            r"municipality|village|river|lake|mountain|asteroid|family name|"
            r"given name|disambiguation|bicycle manufacturer|football club|"
            r"cricket|species of|genus of)\b",
            abstract + " " + heading,
        ):
            best_reject = "ddg_non_company"
            continue
        # Must look company-ish
        if not COMPANYISH_DESC.search(abstract):
            best_reject = "ddg_not_companyish"
            continue
        blurb = acceptable_blurb(abstract, name)
        if not blurb:
            trim = re.split(r"(?<=[.!?])\s+", abstract)
            cand = " ".join(trim[:2])[:400].strip()
            blurb = acceptable_blurb(cand, name)
        if not blurb:
            best_reject = "ddg_unusable"
            continue
        src_tag = "ddg_ia:wikipedia" if "wikipedia.org" in abs_url else "ddg_ia"
        return blurb, src_tag
    return None, best_reject


def fetch_site_blurb_grounded(url: str, company_name: str | None) -> tuple[str | None, str]:
    """Like fetch_site_blurb but requires name grounding vs title/meta/final domain."""
    blurb, note = fetch_site_blurb(url, company_name)
    if not blurb:
        return None, note
    # Re-fetch is expensive; parse domain from note site_meta:host
    host = None
    if note.startswith("site_meta:"):
        host = note.split(":", 1)[1]
    if company_name and host and not domain_aligned(company_name, host):
        # Allow if company name clearly appears in blurb (official site restated)
        if not name_in_text(company_name, blurb):
            return None, "ungrounded_domain"
    if company_name and not name_in_text(company_name, blurb, host or ""):
        # soft: domain alignment alone can suffice when domain tightly matches
        if not (host and domain_aligned(company_name, host)):
            return None, "ungrounded_meta"
    return blurb, note


META_PATS = [
    re.compile(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:description', re.I),
    re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description', re.I),
    re.compile(r'<meta[^>]+name=["\']twitter:description["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:description', re.I),
]


def empty(v) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    return False


def current_desc(o: dict) -> str | None:
    for k in identity._DESC_KEYS:
        if k in o and not empty(o.get(k)):
            return str(o[k]).strip()
    return None


def needs_desc(o: dict) -> bool:
    return current_desc(o) is None


def company_url_of(o: dict) -> str | None:
    return identity.company_url(o)


def domain_of(url: str | None) -> str | None:
    if not url:
        return None
    try:
        net = urlparse(url if "//" in url else "//" + url, scheme="https").netloc.lower()
    except ValueError:
        return None
    net = net.split("@")[-1].split(":")[0]
    return net[4:] if net.startswith("www.") else net or None


def clean_text(t: str) -> str:
    t = htmlmod.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    # strip surrounding quotes
    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        t = t[1:-1].strip()
    return t


def acceptable_blurb(text: str | None, company_name: str | None = None) -> str | None:
    if not text:
        return None
    t = clean_text(text)
    if len(t) < 28 or len(t) > 600:
        return None
    if JUNK_META.match(t):
        return None
    if PARKED.search(t):
        return None
    # too many pipes / SEO keyword stuffing
    if t.count("|") >= 3 or t.count(",") > 12:
        return None
    # reject pure title echoes that are just the company name
    if company_name and t.lower().rstrip(".") == company_name.strip().lower():
        return None
    return t


def extract_meta(html: str) -> str | None:
    # Prefer og:description then name=description
    for pat in META_PATS:
        m = pat.search(html)
        if m:
            return clean_text(m.group(1))
    return None


def fetch_site_blurb(url: str, company_name: str | None) -> tuple[str | None, str]:
    """Return (blurb, source_note). source_note explains reject reason if None."""
    host = domain_of(url)
    if not host:
        return None, "bad_url"
    if FORBIDDEN_HOST.search(host):
        return None, "forbidden_host"
    if not url.startswith("http"):
        url = "https://" + url.lstrip("/")
    try:
        r = requests.get(url, headers=UA, timeout=14, allow_redirects=True)
    except requests.RequestException as e:
        return None, f"fetch_err:{type(e).__name__}"
    if r.status_code >= 400:
        return None, f"http_{r.status_code}"
    final_host = domain_of(r.url) or host
    if FORBIDDEN_HOST.search(final_host):
        return None, "redirect_forbidden"
    body = r.text or ""
    sample = body[:12000]
    if PARKED.search(sample):
        return None, "parked"
    # very empty / challenge pages
    if len(body) < 400 and "cf-browser-verification" in body.lower():
        return None, "challenge"
    meta = extract_meta(body)
    blurb = acceptable_blurb(meta, company_name)
    if not blurb:
        return None, "no_usable_meta"
    # Reject if meta is clearly about a VC fund and company isn't a VC
    if VC_SELF.search(blurb) and company_name and "ventures" not in company_name.lower():
        # allow if company name appears in blurb
        if company_name.split()[0].lower() not in blurb.lower():
            return None, "vc_self_meta"
    return blurb, f"site_meta:{final_host}"


def wd_api(params: dict) -> dict:
    params = {**params, "format": "json"}
    for attempt in range(3):
        try:
            r = requests.get(WD_API, params=params, headers=UA, timeout=25)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            time.sleep(0.8 * (attempt + 1))
    return {}



def wd_is_false_friend(blurb: str) -> bool:
    return bool(re.search(
        r"(?i)\b(collaborative research network|economic project developed|"
        r"packet switching to forward data|syntax highlighter|"
        r"venture capital firm|journal of open source|software described in|"
        r"one main component of the|disambiguation|wikimedia|"
        r"family name|given name|river in|mountain in|"
        r"research network for the study)\b",
        blurb or "",
    ))

def wd_blurb_for(name: str, target_domain: str | None) -> tuple[str | None, str]:
    """Find Wikidata description, verifying via P856 domain when we have a URL."""
    if not name or len(name.strip()) < 2:
        return None, "no_name"
    res = wd_api({
        "action": "wbsearchentities",
        "search": name.strip(),
        "language": "en",
        "type": "item",
        "limit": 8,
    })
    hits = res.get("search") or []
    if not hits:
        return None, "wd_no_hits"
    ids = [h["id"] for h in hits]
    ents = wd_api({
        "action": "wbgetentities",
        "ids": "|".join(ids),
        "props": "claims|descriptions|labels|aliases",
        "languages": "en",
    }).get("entities") or {}

    def label_match(e: dict) -> bool:
        labels = []
        lab = (e.get("labels", {}).get("en") or {}).get("value")
        if lab:
            labels.append(lab)
        for a in (e.get("aliases", {}).get("en") or []):
            if isinstance(a, dict) and a.get("value"):
                labels.append(a["value"])
        n = re.sub(r"[^a-z0-9]", "", name.lower())
        for lab in labels:
            ln = re.sub(r"[^a-z0-9]", "", lab.lower())
            if ln == n or n in ln or ln in n:
                return True
        return False

    # Pass 1: domain-verified
    if target_domain:
        for qid in ids:
            e = ents.get(qid) or {}
            claims = e.get("claims") or {}
            for c in claims.get("P856", []):
                v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
                if isinstance(v, str) and domain_of(v) == target_domain:
                    desc = (e.get("descriptions", {}).get("en") or {}).get("value")
                    blurb = acceptable_blurb(desc, name)
                    if blurb:
                        if wd_is_false_friend(blurb):
                            continue
                        return blurb, f"wikidata:{qid}:P856"
                    # domain matched but WD desc useless — still trusted site
                    return None, f"wd_domain_ok_no_desc:{qid}"

    # Pass 2: org-typed + label match (no URL case, or URL didn't match)
    for qid in ids:
        e = ents.get(qid) or {}
        claims = e.get("claims") or {}
        p31 = []
        for c in claims.get("P31", []):
            v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
            if isinstance(v, dict) and v.get("id"):
                p31.append(v["id"])
        if PERSON_P31.intersection(p31) and not ORG_P31.intersection(p31):
            continue
        desc = (e.get("descriptions", {}).get("en") or {}).get("value")
        if not desc:
            continue
        is_org = bool(ORG_P31.intersection(p31)) or bool(COMPANYISH_DESC.search(desc))
        if not is_org:
            continue
        if not label_match(e):
            continue
        # If we have a target domain and entity has a DIFFERENT P856, skip (mis-attribution)
        sites = []
        for c in claims.get("P856", []):
            v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
            if isinstance(v, str):
                sites.append(domain_of(v))
        if target_domain and sites and target_domain not in sites:
            continue
        blurb = acceptable_blurb(desc, name)
        if not blurb:
            continue
        # Reject non-company WD descriptions (games, medals, places, false friends)
        if re.search(
            r"(?i)\b(medal|award|decoration|video game|adventure game|"
            r"interactive fiction|song|album|film\b|movie|television|"
            r"municipality|village|river|asteroid|family name|given name|"
            r"bus services? company in|syntax highlighter|"
            r"application framework for Java)\b",
            blurb,
        ):
            continue
        if not target_domain:
            # No-URL: require EXACT label/alias match AND org-typed P31
            lab = (e.get("labels", {}).get("en") or {}).get("value") or ""
            aliases = [a.get("value", "") for a in (e.get("aliases", {}).get("en") or [])]
            exact = any(
                re.sub(r"[^a-z0-9]", "", x.lower()) == re.sub(r"[^a-z0-9]", "", name.lower())
                for x in [lab] + aliases
            )
            if not exact:
                continue
            if not ORG_P31.intersection(p31):
                continue
            # Tighten: short / single-token names without URL are too ambiguous
            if len(re.sub(r"[^a-z0-9]", "", name.lower())) < 6:
                continue
            if len(sig_tokens(name)) <= 1 and len(re.sub(r"[^a-z0-9]", "", name.lower())) < 8:
                continue
        if wd_is_false_friend(blurb):
            continue
        return blurb, f"wikidata:{qid}"
    return None, "wd_no_match"


def dataset_files(firms: list[str] | None):
    files = sorted(DATA.glob("*_companies.json"))
    files = [p for p in files if p.name != "all_companies.json"]
    if firms:
        want = set(firms)
        files = [p for p in files if (identity.slug_from_file(p.name) or p.stem) in want]
    # priority order
    def sort_key(p: Path):
        slug = identity.slug_from_file(p.name) or p.stem
        try:
            return (0, PRIORITY.index(slug))
        except ValueError:
            return (1, slug)

    return sorted(files, key=sort_key)


def inventory(files):
    total = miss = 0
    by_firm = Counter()
    firm_totals = {}
    for p in files:
        data = json.load(open(p))
        slug = identity.slug_from_file(p.name) or p.stem
        firm_totals[slug] = len(data)
        for o in data:
            total += 1
            if needs_desc(o):
                miss += 1
                by_firm[slug] += 1
    return {
        "total": total,
        "miss_desc": miss,
        "cov_desc": (total - miss) / total if total else 0,
        "by_firm_desc": dict(by_firm),
        "firm_totals": firm_totals,
    }


def resolve_one(o: dict, firm_slug: str | None = None) -> dict:
    """Attempt to find a description for one empty company record.

    Safety:
      - Existing company_url: ONLY that site's meta, else domain-verified Wikidata.
        Never fall through to Clearbit/DDG (dead URLs must not invent new domains).
      - No URL: Clearbit exact-name + domain-aligned + name grounded in meta/title;
        else DDG IA (strict companyish, name len>=6); else Wikidata strict.
      - Leave empty if uncertain.
    """
    name = identity.company_name(o)
    url = company_url_of(o)
    firm_name = _FIRM_NAMES.get(firm_slug or "", firm_slug)
    result = {
        "company": name,
        "url": url,
        "description": None,
        "source": None,
        "reject": None,
        "firm": firm_slug,
    }
    rejects: list[str] = []

    # --- Path A: known URL from firm scrape (trusted host) ---
    if url:
        blurb, note = fetch_site_blurb(url, name)
        if blurb:
            # Reject aged-domain / marketplace junk even on "official" URL
            if re.search(r"(?i)premium aged domain|buy this domain|domain for sale|verified backlinks", blurb):
                rejects.append("junk_meta")
            else:
                result["description"] = blurb
                result["source"] = note
                return result
        else:
            rejects.append(note)
        blurb, note = wd_blurb_for(name or "", domain_of(url))
        if blurb:
            result["description"] = blurb
            result["source"] = note
            return result
        rejects.append(note)
        result["reject"] = "|".join(rejects)[:300]
        return result

    # --- Path B: name-only (no URL) — discovery with strict grounding ---
    if name:
        dom, note = clearbit_domain(name)
        if dom:
            # Fetch title+meta; require name grounding in title or blurb
            try:
                r = requests.get(
                    "https://" + dom,
                    headers=UA,
                    timeout=14,
                    allow_redirects=True,
                )
            except requests.RequestException as e:
                rejects.append(f"{note}|fetch_err:{type(e).__name__}")
                r = None
            if r is not None and r.status_code < 400:
                final = domain_of(r.url) or dom
                if FORBIDDEN_HOST.search(final or ""):
                    rejects.append(f"{note}|redirect_forbidden")
                elif not domain_aligned(name, final):
                    rejects.append(f"{note}|redirect_unaligned:{final}")
                elif tld_rank(final) >= 40 and len(norm_alnum(name)) < 8 and len(sig_tokens(name)) <= 1:
                    rejects.append(f"{note}|weak_tld_final:{final}")
                else:
                    body = r.text or ""
                    if PARKED.search(body[:12000]):
                        rejects.append(f"{note}|parked")
                    else:
                        title = extract_title(body)
                        meta = extract_meta(body)
                        blurb = acceptable_blurb(meta, name)
                        if blurb and re.search(
                            r"(?i)premium aged domain|buy this domain|domain for sale|"
                            r"verified backlinks|related searches|"
                            r"#1 real estate|real estate agent|thank you for supporting|"
                            r"laguna niguel|personal branding|"
                            r"we want to express our heartfelt|"
                            r"avaya professional services|perfect domain name for your idea|"
                            r"synthesia is your piano tutor|"
                            r"retail operations software from zipline|"
                            r"commercial real estate finance and lending|"
                            r"team behind mosaic ventures|"
                            r"find quality manufacturers|"
                            r"paylocity, a leader in cloud-based|"
                            r"cellular iot management from cisco|"
                            r"map multiple locations, get transit|"
                            r"trusted by the world.s leading companies\s*$",
                            blurb,
                        ):
                            rejects.append(f"{note}|junk_meta")
                            blurb = None
                        # Name must appear in title or blurb (blocks Seatme→SA tickets,
                        # Sense360→Sense home, Berry Health→symposium, etc.)
                        # Grounding: prefer name in blurb. If domain tightly matches
                        # the company name (cameo.com / classpass.com), allow meta
                        # that omits the brand (common for consumer apps).
                        if blurb and not name_in_text(name, blurb):
                            tight = domain_aligned(name, final) and tld_rank(final) <= 12
                            title_ok = (
                                tld_rank(final) <= 12
                                and title
                                and name_in_text(name, title)
                            )
                            if not (tight or title_ok):
                                rejects.append(f"{note}|ungrounded_meta")
                                blurb = None
                        # Reject VC-fund self pages for portfolio companies
                        if blurb and VC_SELF.search(blurb) and "ventures" not in (name or "").lower():
                            if not name_in_text(name, blurb):
                                rejects.append(f"{note}|vc_self")
                                blurb = None
                        if blurb:
                            result["description"] = blurb
                            result["source"] = f"clearbit:site_meta:{final}"
                            return result
                        if not blurb:
                            rejects.append(f"{note}|no_usable_meta")
            elif r is not None:
                rejects.append(f"{note}|http_{r.status_code}")
        else:
            rejects.append(note)

        blurb, note = ddg_ia_blurb(name, firm_name)
        if blurb:
            # Extra: heading should roughly match company name
            result["description"] = blurb
            result["source"] = note
            return result
        rejects.append(note)

    blurb, note = wd_blurb_for(name or "", None)
    if blurb:
        # Extra reject: pure research-network / historical project false friends
        if re.search(
            r"(?i)\b(collaborative research network|economic project developed|"
            r"packet switching to forward data|syntax highlighter|"
            r"venture capital firm|journal of open source|software described in|"
            r"one main component of the|disambiguation|wikimedia|"
            r"family name|given name|river in|mountain in)\b",
            blurb,
        ):
            rejects.append("wd_false_friend")
        else:
            result["description"] = blurb
            result["source"] = note
            return result
    else:
        rejects.append(note)

    result["reject"] = "|".join(rejects)[:300]
    return result


def process_firm(path: Path, limit: int | None, workers: int, dry_run: bool) -> dict:
    slug = identity.slug_from_file(path.name) or path.stem
    data = json.load(open(path))
    targets = []
    for i, o in enumerate(data):
        if needs_desc(o):
            targets.append((i, o))
    if limit is not None:
        targets = targets[:limit]

    fills = []
    rejects = Counter()
    if not targets:
        return {"slug": slug, "targets": 0, "filled": 0, "fills": [], "rejects": {}}

    def work(item):
        i, o = item
        try:
            r = resolve_one(o, firm_slug=slug)
            r["index"] = i
            return r
        except Exception as e:
            return {
                "index": i,
                "company": identity.company_name(o),
                "url": company_url_of(o),
                "description": None,
                "source": None,
                "reject": f"exc:{type(e).__name__}",
            }

    results = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(work, t): t for t in targets}
        for fut in as_completed(futs):
            results.append(fut.result())

    changed = False
    for r in results:
        if r.get("description"):
            i = r["index"]
            # Only fill if still empty (never overwrite)
            if needs_desc(data[i]):
                data[i]["description"] = r["description"]
                fills.append({
                    "company": r.get("company"),
                    "description": r["description"],
                    "source": r.get("source"),
                    "url": r.get("url"),
                })
                changed = True
        else:
            rejects[r.get("reject") or "unknown"] += 1

    if changed and not dry_run:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    return {
        "slug": slug,
        "targets": len(targets),
        "filled": len(fills),
        "fills": fills,
        "rejects": dict(rejects),
    }


def log(msg: str = ""):
    print(msg, flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--firms", type=str, default=None, help="comma-separated firm slugs")
    ap.add_argument("--priority-only", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="max empties per firm")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    firms = None
    if args.firms:
        firms = [s.strip() for s in args.firms.split(",") if s.strip()]
    elif args.priority_only:
        firms = list(PRIORITY)

    files = dataset_files(firms)
    before = inventory(files if firms else dataset_files(None))
    # Always inventory full corpus for before stats when not firm-restricted report
    before_all = inventory(dataset_files(None))

    log(f"BEFORE all: total={before_all['total']} miss={before_all['miss_desc']} "
          f"cov={before_all['cov_desc']*100:.2f}%")
    log(f"Processing {len(files)} firm files; workers={args.workers}")

    firm_results = []
    total_filled = 0
    for p in files:
        slug = identity.slug_from_file(p.name) or p.stem
        n_miss = before_all["by_firm_desc"].get(slug, 0)
        if n_miss == 0 and not firms:
            continue
        log(f"\n== {slug} ({n_miss} missing) ==")
        try:
            res = process_firm(p, args.limit, args.workers, args.dry_run)
        except Exception:
            traceback.print_exc()
            res = {"slug": slug, "targets": 0, "filled": 0, "fills": [], "rejects": {"exc": 1}}
        firm_results.append(res)
        total_filled += res["filled"]
        log(f"  filled {res['filled']}/{res['targets']}")
        if res["fills"][:2]:
            for f in res["fills"][:2]:
                log(f"    + {f['company']}: {f['description'][:90]}… [{f['source']}]")

    after_all = inventory(dataset_files(None))
    report = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "before": before_all,
        "after": after_all,
        "filled_total": total_filled,
        "dry_run": args.dry_run,
        "firms": [r["slug"] for r in firm_results],
        "by_firm": {
            r["slug"]: {
                "targets": r["targets"],
                "filled": r["filled"],
                "rejects": r["rejects"],
                "sample_fills": r["fills"][:5],
            }
            for r in firm_results
        },
    }
    out = ART / "fill_descriptions_web_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    log(f"\nAFTER all: total={after_all['total']} miss={after_all['miss_desc']} "
          f"cov={after_all['cov_desc']*100:.2f}%")
    log(f"Filled: {total_filled}")
    log(f"Wrote {out}")


if __name__ == "__main__":
    main()
