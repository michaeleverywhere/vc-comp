"""Shared helpers for accelerator scrapers (Accelerator Data table).

Record schema (one per company per accelerator), mirrored 1:1 onto the Airtable
"Accelerator Data" columns by accelerators/airtable_rows.py:
  name, description, website, team, round, amount_raised, date (batch/cohort),
  verticals (accelerator's own labels), investors (accelerator [+ co-investors]),
  source (accelerator site label), everywhere_tags, source_url

Rules (Michael's standing rules): only publish what the accelerator's own site /
demo-day pages / the company's own site publish; never Crunchbase / LinkedIn /
PitchBook; tagging is keyword-only via automation/tags.py (no LLM), max 4,
no AI sector.
"""
from __future__ import annotations

import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "automation"))
import tags  # noqa: E402

DATA_DIR = os.path.join(ROOT, "data", "accelerators")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126 Safari/537.36"}

# Accelerator-label -> Everywhere tag, applied as judgment on top of the keyword
# classifier (labels are the accelerator's own published industry tags).
LABEL_MAP = {
    "fintech": "FinTech / Insurance", "insurance": "FinTech / Insurance",
    "banking": "FinTech / Insurance", "payments": "FinTech / Insurance",
    "healthcare": "Health", "health": "Health", "medical devices": "Health",
    "healthcare it": "Health", "digital health": "Health",
    "biotech": "BioTech", "drug discovery": "BioTech", "therapeutics": "BioTech",
    "security": "Cybersecurity", "cybersecurity": "Cybersecurity",
    "developer tools": "Dev Tools / Cloud", "infrastructure": "Dev Tools / Cloud",
    "engineering, product and design": "Dev Tools / Cloud",
    "consumer": "Consumer", "education": "Consumer", "edtech": "Consumer",
    "food and beverage": "CPG", "consumer products": "CPG", "cpg": "CPG",
    "recruiting and talent": "Future of Work", "human resources": "Future of Work",
    "hr tech": "Future of Work", "future of work": "Future of Work",
    "productivity": "Future of Work",
    "transportation services": "Transportation / Mobility",
    "automotive": "Transportation / Mobility", "mobility": "Transportation / Mobility",
    "transportation": "Transportation / Mobility",
    "legal": "RegTech/Gov/Legal", "government": "RegTech/Gov/Legal",
    "legaltech": "RegTech/Gov/Legal", "govtech": "RegTech/Gov/Legal",
    "hard tech": "Deeptech / Robotics / AR/VR", "robotics": "Deeptech / Robotics / AR/VR",
    "aviation and space": "Deeptech / Robotics / AR/VR",
    "aerospace": "Deeptech / Robotics / AR/VR", "space": "Deeptech / Robotics / AR/VR",
    "defense": "Deeptech / Robotics / AR/VR", "hardware": "Deeptech / Robotics / AR/VR",
    "ar/vr": "Deeptech / Robotics / AR/VR", "deep tech": "Deeptech / Robotics / AR/VR",
    "manufacturing and robotics": "Deeptech / Robotics / AR/VR",
    "analytics": "Data & Analytics", "data": "Data & Analytics",
    "supply chain and logistics": "Logistics / Supply Chain",
    "logistics": "Logistics / Supply Chain", "supply chain": "Logistics / Supply Chain",
    "crypto / web3": "Web3 / Crypto", "crypto": "Web3 / Crypto", "web3": "Web3 / Crypto",
    "blockchain": "Web3 / Crypto",
    "real estate and construction": "PropTech", "proptech": "PropTech",
    "real estate": "PropTech", "housing and real estate": "PropTech",
    "gaming": "Gaming / Media / Entertainment", "media": "Gaming / Media / Entertainment",
    "content": "Gaming / Media / Entertainment", "entertainment": "Gaming / Media / Entertainment",
    "climate": "Climate / Sustainability", "energy": "Climate / Sustainability",
    "climate tech": "Climate / Sustainability", "sustainability": "Climate / Sustainability",
    "agriculture": "Climate / Sustainability", "agtech": "Climate / Sustainability",
    "cleantech": "Climate / Sustainability",
}


def tag(name, description, labels=None) -> list:
    """Keyword tags (automation/tags.py) + accelerator-label mapping, max 4."""
    labels = [l for l in (labels or []) if l]
    out = []
    for l in labels:
        t = LABEL_MAP.get(l.strip().lower())
        if t and t not in out:
            out.append(t)
    for t in tags.classify(name, description, labels):
        if t not in out:
            out.append(t)
    return [t for t in out if t in tags.TAGS][:4]


def norm_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = s.lower().strip()
    s = re.sub(r"\b(inc|llc|ltd|corp|co|gmbh|sas|bv|plc)\b\.?", "", s)
    return re.sub(r"[^a-z0-9]+", "", s)


def dedupe(records):
    """Dedupe by normalized name, merging non-empty fields (first wins)."""
    seen = {}
    for r in records:
        k = norm_name(r.get("name"))
        if not k:
            continue
        if k not in seen:
            seen[k] = r
        else:
            cur = seen[k]
            for f, v in r.items():
                if v and not cur.get(f):
                    cur[f] = v
                elif f == "date" and v and cur.get(f) and v not in cur[f]:
                    cur[f] = cur[f] + "; " + v
    return list(seen.values())


def clean(s):
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s)).strip()


BANNED = re.compile(r"crunchbase\.com|linkedin\.com|pitchbook\.com", re.I)


def save(slug, records, meta=None):
    for r in records:            # never keep banned-source URLs as data fields
        for f in ("website", "source_url"):
            if r.get(f) and BANNED.search(r[f]):
                r[f] = ""
        r["website"] = r.get("website") or ""
        r["linkedin_url"] = norm_linkedin(r.get("linkedin_url"))
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"{slug}_companies.json")
    payload = {"accelerator": slug, "count": len(records), **(meta or {}),
               "companies": records}
    with open(path, "w") as f:
        json.dump(payload, f, indent=1, ensure_ascii=False)
    print(f"[{slug}] saved {len(records)} -> {path}")
    return path


LI_RE = re.compile(r'https?://(?:[a-z]{2,3}\.)?linkedin\.com/(?:company|school|showcase)/[A-Za-z0-9_%.\-]+/?', re.I)


def norm_linkedin(u):
    """Canonical company LinkedIn URL (only ever taken from an accelerator page or
    the company's own site; LinkedIn itself is never fetched)."""
    if not u:
        return ""
    u = u.strip()
    if not u.startswith("http"):
        u = "https://" + u.lstrip("/")
    m = LI_RE.match(u.split("?")[0])
    if not m:
        return ""
    path = re.sub(r"^https?://[^/]+", "", m.group(0)).rstrip("/")
    return "https://www.linkedin.com" + path


def site_info(url, name=None, timeout=15):
    """(description, linkedin_url) from the company's OWN homepage."""
    return site_description(url, timeout, name, want_li=True)


def site_description(url, timeout=15, name=None, want_li=False):
    """<meta name=description> / og:description from the company's OWN site."""
    import html as _h
    import requests
    empty = ("", "") if want_li else ""
    if not url or BANNED.search(url):
        return empty
    try:
        r = requests.get(url if url.startswith("http") else "https://" + url,
                         headers=UA, timeout=timeout, allow_redirects=True)
        if r.status_code >= 400 or BANNED.search(r.url):
            return empty
        s = r.text[:300000]
    except Exception:
        return empty
    if want_li:
        d = _desc_from_html(s, name)
        li = ""
        if d or not name:      # only trust links on a page that is really the company's
            m = LI_RE.search(s)
            li = norm_linkedin(m.group(0)) if m else ""
        return d, li
    return _desc_from_html(s, name)


def _desc_from_html(s, name):
    import html as _h
    pats = []
    for q in ('"', "'"):
        pats += [rf'<meta[^>]+name=["\']description["\'][^>]+content={q}([^{q}]{{20,}}){q}',
                 rf'<meta[^>]+content={q}([^{q}]{{20,}}){q}[^>]+name=["\']description',
                 rf'<meta[^>]+property=["\']og:description["\'][^>]+content={q}([^{q}]{{20,}}){q}']
    for pat in pats:
        m = re.search(pat, s, re.I)
        if m:
            d = clean(_h.unescape(m.group(1)))
            if re.search(r"meta description|lorem ipsum|just another wordpress|coming soon|"
                         r"page not found|domain (is )?for sale|access denied|casino|pokies|"
                         r"slots?\b|betting|jackpot|\bbonus\b", d, re.I):
                return ""
            if name:   # guard against expired domains now serving someone else
                title = (re.search(r"<title[^>]*>(.*?)</title>", s, re.I | re.S) or [None, ""])[1]
                hay = norm_name(title + " " + d)
                toks = [norm_name(t) for t in re.split(r"[\s.\-]+", name) if len(norm_name(t)) >= 3]
                if toks and not any(t in hay for t in toks):
                    return ""
            return d
    return ""


def enrich_from_sites(records, workers=12):
    """From each company's own website: fill a blank description and a blank
    linkedin_url (only a linkedin.com/company link the site itself publishes)."""
    from concurrent.futures import ThreadPoolExecutor
    todo = [r for r in records if r.get("website") and (not r.get("description") or not r.get("linkedin_url"))]
    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(lambda r: site_info(r["website"], name=r.get("name")), todo))
    n = 0
    for r, (d, li) in zip(todo, res):
        if d and not r.get("description"):
            r["description"] = d
            r["description_source"] = "company website meta description"
            n += 1
        if li and not r.get("linkedin_url"):
            r["linkedin_url"] = li
            r["linkedin_source"] = "company website"
    return n
