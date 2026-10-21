"""Builds data/companies_unique.json (+ companies_unique_2.json, _3 ... overflow parts) and
data/companies_unique_index.json: ONE row per real company across every Private Comps firm
file (data/*_companies.json) and every accelerator file (data/accelerators/*_companies.json).

Michael 2026-10-21: "one unique row ... with all details on the company, like its core identity
and all transaction information". Each unique row carries
  - core identity: name, website, domain, description, everywhere_tags, verticals, location,
    status, exited, founded, team (every conflicting value kept in <field>_alternates)
  - relationships: `backers` = one entry per source row (every VC firm / accelerator that lists the
    company, with stage, first_invested, listing dates, batch ...), plus vc_firms / accelerators lists
  - transactions: funding_rounds (union of every source row + funding_all/records, deduped on
    round family + date), grants, total_raised, last_round_*, notable_investors, funding_source_urls ...

This is an ADDITIONAL file. It never edits or removes any firm/accelerator dataset or the per-firm
master (all_companies*.json). Nothing is invented: every value comes from a source row or a
funding research record. No company is dropped: every named source row maps to exactly one unique
row (validated before writing; the build aborts otherwise).

Identity key (in order):
  1. normalized website domain, when the host is a real company site (not youtube, maps.app.goo.gl,
     substack, googleusercontent, linkedin, twitter/x, crunchbase, press wires, app stores ...) and
     the names on that domain agree. A host carrying 3+ unrelated names (a portfolio/CDN/newsletter
     host) is treated as junk. On a host with 2 unrelated names, the one(s) matching the domain label
     keep the domain; the other falls back to its name.
  2. otherwise the normalized name ("name:<norm>"). A name-only row joins a domain company only when
     exactly one domain company carries that exact normalized name; if several do it stays separate
     and lists them in `possible_matches` (never merged on a guess).

Fast and offline (a few seconds); rerun after every funding batch:
    python3 automation/unique_builder.py [--records /workspace/funding_all/records] [--check]
--check validates and prints stats without writing.
"""
from __future__ import annotations

import argparse
import collections
import difflib
import glob
import json
import os
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import identity  # noqa: E402
import master_builder  # noqa: E402
import names  # noqa: E402

REPO = _HERE.parent
DATA = REPO / "data"
ACCEL = DATA / "accelerators"
DEFAULT_RECORDS = "/workspace/funding_all/records"
OUT_BASE = "companies_unique"
INDEX_FILENAME = "companies_unique_index.json"
PART_LIMIT_BYTES = 40_000_000
_PART_RE = re.compile(r"^companies_unique(?:_(\d+))?\.json$")

BANNED = ("crunchbase.com", "linkedin.com", "pitchbook.com")
# hosts that are never a company's own site -> fall back to the name
JUNK_HOSTS = {
    "youtube.com", "youtu.be", "maps.app.goo.gl", "goo.gl", "maps.google.com", "google.com",
    "googleusercontent.com", "lh3.googleusercontent.com", "squarespace-cdn.com", "substack.com",
    "linkedin.com", "twitter.com", "x.com", "crunchbase.com", "pitchbook.com", "facebook.com",
    "instagram.com", "wikipedia.org", "linktr.ee", "medium.com", "techcrunch.com", "prnewswire.com",
    "businesswire.com", "globenewswire.com", "apps.apple.com", "play.google.com", "bit.ly",
    "angel.co", "wellfound.com", "tiktok.com", "vimeo.com", "forbes.com", "bloomberg.com",
    "reuters.com", "wsj.com", "nytimes.com", "finsmes.com", "notion.site", "sites.google.com",
    "drive.google.com", "docs.google.com", "dropbox.com", "ycombinator.com", "f6s.com",
    "tracxn.com", "dealroom.co", "cbinsights.com", "producthunt.com", "github.com", "t.co",
    "lnkd.in", "tinyurl.com", "about.me", "wix.com", "wixsite.com", "squarespace.com",
    "cloudfront.net", "amazonaws.com", "wp.com", "gravatar.com", "imgur.com", "calendly.com",
    "eventbrite.com", "zoom.us", "typeform.com", "airtable.com", "example.com", "localhost",
}
PLATFORM_SUFFIXES = ("substack.com", "googleusercontent.com", "squarespace-cdn.com", "medium.com",
                     "wixsite.com", "cloudfront.net", "amazonaws.com", "notion.site", "linkedin.com",
                     "goo.gl", "youtube.com", "facebook.com", "crunchbase.com")
TLD2 = {"co", "com", "org", "net", "ac", "gov", "edu", "or", "ne", "go"}

LEGAL = re.compile(r"\b(inc|incorporated|llc|l\.l\.c|ltd|limited|corp|corporation|co|gmbh|ag|sa|sas|"
                   r"bv|nv|plc|pbc|srl|oy|ab|pty|pvt|private|spa|kk|kft|sp z o o)\b\.?$")
CORE_SUFFIX = re.compile(r"\b(inc|incorporated|llc|ltd|limited|corp|corporation|co|company|gmbh|ag|sa|sas|"
                         r"bv|plc|pbc|technologies|technology|labs|holdings|group|ai|hq|app|the)\b")


# ---------------- normalizers ----------------
def domain(u) -> str:
    u = (u or "").lower().strip() if isinstance(u, str) else ""
    u = re.sub(r"^[a-z]+://", "", u)
    u = re.sub(r"^www\d?\.", "", u)
    return u.split("/")[0].split("?")[0].split("#")[0].split(":")[0].strip(". ")


def host_ok(h: str) -> bool:
    if not h or "." not in h or " " in h or "@" in h:
        return False
    if h in JUNK_HOSTS or any(h.endswith("." + j) for j in JUNK_HOSTS):
        return False
    if any(h == p or h.endswith("." + p) for p in PLATFORM_SUFFIXES):
        return False
    if not re.match(r"^[a-z0-9\-\.\u00a1-\uffff]+$", h) or re.match(r"^\d+(\.\d+){3}$", h):
        return False
    return True


def label(h: str) -> str:
    p = h.split(".")
    if len(p) >= 3 and p[-2] in TLD2:
        lab = p[-3]
    elif len(p) >= 2:
        lab = p[-2]
    else:
        lab = p[0]
    return re.sub(r"[^a-z0-9]", "", lab)


def norm_name(s) -> str:
    """Conservative name key: case/punctuation/legal-suffix insensitive only."""
    s = (s or "").strip().lower().replace("&", " and ")
    s = re.sub(r"^the\s+", "", s)
    prev = None
    while prev != s:
        prev = s
        s = LEGAL.sub("", s.strip(" ,.")).strip(" ,.")
    k = re.sub(r"[\W_]+", "", s)
    return k or re.sub(r"\s+", "", (prev or "").lower())


def core(s) -> str:
    s = (s or "").lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = CORE_SUFFIX.sub(" ", s)
    return re.sub(r"\s+", "", s)


def compatible(a: str, b: str, lab: str = "") -> bool:
    """Two names on the SAME domain describe the same company?"""
    if not a or not b:
        return False
    if a == b:
        return True
    if min(len(a), len(b)) >= 3 and (a in b or b in a):
        return True
    if lab and len(lab) >= 3 and lab in a and lab in b:
        return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.85


def matches_label(n: str, lab: str) -> bool:
    return bool(n and lab and min(len(n), len(lab)) >= 3 and (lab in n or n in lab))


def host_label(dom: str) -> str:
    """label, or the whole domain without dots when the label is tiny (x.ai -> 'xai', 17.live -> '17live')."""
    lab = label(dom)
    return lab if len(lab) >= 3 else re.sub(r"[^a-z0-9]", "", dom)


PLACEHOLDER = re.compile(r"^(stealth|stealthmode|stealthstartup|stealthcompany|stealthco|stealthmodestartup|"
                         r"undisclosed|undisclosedcompany|confidential|unnamed|tbd|tba|na|none|unknown|"
                         r"privatecompany|newco|comingsoon)$")


def nonempty(v) -> bool:
    return master_builder._nonempty(v)


# ---------------- funding helpers (mirror /workspace/funding_all/lib.py) ----------------
ROUND_MAP = [
    (r"pre[- ]?series[- ]?a", "Pre-Series A"), (r"pre[- ]?seed", "Pre-Seed"), (r"\bseed", "Seed Round"),
    (r"series ([a-h])\b", None), (r"\bangel", "Angel Round"), (r"grant|sbir|sttr|non[- ]dilutive", "Grant"),
    (r"convertible|safe\b|note", "Convertible Note"), (r"debt|credit|loan|venture debt", "Debt Financing"),
    (r"equity crowdfunding|crowdfund", "Equity Crowdfunding"), (r"growth", "Growth Round"),
    (r"strategic|corporate", "Strategic"), (r"private equity", "Private Equity Round"),
    (r"pre[- ]?ipo", "Pre-IPO"), (r"secondary|tender", "Secondary Market"), (r"venture", "Venture Round")]
EQUITY_EXCLUDE = re.compile(r"grant|debt|loan|credit|ipo|spac|secondary|tender|token|ico\b", re.I)
STATUS_ORDER = ["no public funding", "grants only", "crowdfunding only", "pre-seed or angel only",
                "unclear-round-type", "seed+"]
FUNDING_SCALARS = ("total_raised", "total_raised_currency", "total_raised_basis", "last_round_type",
                   "last_round_amount", "last_round_currency", "last_round_date")


def round_family(stage) -> str:
    s = (stage or "").lower() if isinstance(stage, str) else ""
    opt = "Funding Round"
    for rx, o in ROUND_MAP:
        m = re.search(rx, s)
        if m:
            opt = f"Series {m.group(1).upper()}" if o is None else o
            break
    o = opt.lower()
    if "pre" in o and "seed" in o and "series" not in o:
        return "preseed"
    if "seed" in o:
        return "seed"
    m = re.search(r"series ([a-z])", o)
    return "series" + m.group(1) if m else o


def banned(u) -> bool:
    h = domain(u)
    return any(b in h for b in BANNED)


def _dkey(d):
    return (d or "").ljust(10, "~")


def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return None


def merge_rounds(rounds: list[dict]) -> list[dict]:
    """Union rounds, one per round family + date (a month-only date matches any day in that month;
    an undated round merges only with a same-family round of the same amount). Conflicting values
    are kept in <field>_alternates; investors/source urls are unioned."""
    out: list[dict] = []
    for r in rounds:
        if not isinstance(r, dict):
            continue
        r = dict(r)
        fam = round_family(r.get("stage"))
        d = (r.get("date") or "") if isinstance(r.get("date"), str) else str(r.get("date") or "")
        hit = None
        for m in out:
            if m["_fam"] != fam:
                continue
            md = m.get("date") or ""
            if d and md:
                if d == md or d.startswith(md) or md.startswith(d):
                    hit = m
                    break
            elif _num(r.get("amount")) is not None and _num(r.get("amount")) == _num(m.get("amount")):
                hit = m
                break
            elif not d and not md and (r.get("amount") in (None, "") or m.get("amount") in (None, "")):
                hit = m
                break
        if hit is None:
            r["_fam"] = fam
            if r.get("source_url"):
                r["source_urls"] = [r["source_url"]]
            out.append(r)
            continue
        if len(d) > len(hit.get("date") or ""):
            hit["date"] = d
        for k, v in r.items():
            if k in ("date", "_fam"):
                continue
            if not nonempty(v):
                continue
            cur = hit.get(k)
            if isinstance(v, list):
                lst = list(cur or []) if isinstance(cur, list) else ([cur] if nonempty(cur) else [])
                for x in v:
                    if x not in lst:
                        lst.append(x)
                hit[k] = lst
            elif not nonempty(cur):
                hit[k] = v
            elif cur != v:
                if k == "source_url":
                    su = hit.setdefault("source_urls", [cur])
                    if v not in su:
                        su.append(v)
                else:
                    alts = hit.setdefault(k + "_alternates", [])
                    if v not in alts:
                        alts.append(v)
    for m in out:
        m.pop("_fam", None)
        if "source_urls" in m:
            m["source_urls"] = [u for u in dict.fromkeys(m["source_urls"]) if u and not banned(u)]
            if len(m["source_urls"]) <= 1:
                m.pop("source_urls")
    out.sort(key=lambda r: _dkey(r.get("date")))
    return out


def summarize(rounds, stated):
    eq = [r for r in rounds if not EQUITY_EXCLUDE.search(r.get("stage") or "")]
    out = {}
    if eq:
        dated = [r for r in eq if r.get("date")]
        last = max(dated, key=lambda r: _dkey(r["date"])) if dated else eq[-1]
        out.update(last_round_type=last.get("stage") or None, last_round_amount=last.get("amount"),
                   last_round_currency=last.get("currency") if last.get("amount") is not None else None,
                   last_round_date=last.get("date") or None)
        amts = [r for r in eq if _num(r.get("amount")) is not None]
        curs = {r.get("currency") or "USD" for r in amts}
        if amts and len(curs) == 1:
            out.update(total_raised=round(sum(_num(r["amount"]) for r in amts)),
                       total_raised_currency=curs.pop(), total_raised_basis="sum_of_sourced_rounds")
    if isinstance(stated, dict) and _num(stated.get("amount")):
        if not out.get("total_raised") or _num(stated["amount"]) >= out["total_raised"]:
            out.update(total_raised=stated["amount"], total_raised_currency=stated.get("currency", "USD"),
                       total_raised_basis="stated")
    inv = []
    for r in rounds:
        for x in (r.get("lead_investors") or []) + (r.get("investors") or []):
            if isinstance(x, str) and x and x not in inv:
                inv.append(x)
    return out, inv


# ---------------- loading ----------------
_LOC = master_builder._LOC_KEYS
_FIRST = master_builder._FIRST_KEYS
FUND_KEYS = master_builder.FUNDING_KEYS + ("stated_total_raised",)


def _accel_names() -> dict:
    try:
        q = json.loads((REPO / "accelerators" / "queue.json").read_text(encoding="utf-8"))
        return {a["slug"]: a.get("name") or a["slug"] for a in q.get("accelerators", []) if a.get("slug")}
    except Exception:  # noqa: BLE001
        return {}


ACCEL_IDENTITY = {"name", "website", "description", "everywhere_tags", "verticals", "location", "status",
                  "team", "linkedin_url", "founded", "founded_year", "is_exit", "accelerator"}
ACCEL_FIRST = ("first_invested", "batch_date", "most_recent_batch", "cohort_year", "year_joined",
               "selection_date", "first_session_year")


def load_rows():
    """Every named source row as a normalized dict with a stable ref '<file>#<index>'."""
    rows, skipped = [], []
    for path in sorted(p for p in DATA.glob("*.json")
                       if not master_builder.is_master_file(p.name) and identity.slug_from_file(p.name)):
        slug = identity.slug_from_file(path.name)
        firm = names.display_name(path.name)
        recs = master_builder._load_dataset(path)
        for i, r in enumerate(recs):
            if not isinstance(r, dict):
                continue
            n = identity.company_name(r)
            ref = f"data/{path.name}#{i}"
            if not n:
                skipped.append(ref)
                continue
            row = {"ref": ref, "type": "vc", "backer": firm, "backer_slug": slug, "name": n,
                   "url": identity.company_url(r), "description": identity.company_desc(r),
                   "everywhere_tags": r.get("everywhere_tags") or [], "exited": identity.is_exited(r),
                   "location": master_builder._first_present(r, _LOC),
                   "stage": master_builder._stage_of(r),
                   "first_invested": master_builder._first_present(r, _FIRST),
                   "status": master_builder._status_of(r), "fund": {}, "rel": {}}
            for k in ("listed_on_site", "first_seen", "last_seen", "delisted_date"):
                if k in r:
                    row["rel"][k] = r[k]
            for k in FUND_KEYS:
                for kk in (k, k + "_public"):
                    if kk in r:
                        row["fund"][kk] = r[kk]
            rows.append(row)
    an = _accel_names()
    for path in sorted(ACCEL.glob("*_companies.json")):
        if path.name.startswith("all_"):
            continue
        slug = path.name[: -len("_companies.json")]
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            print(f"[unique_builder] WARNING: could not read {path.name}")
            continue
        cs = d.get("companies") if isinstance(d, dict) else d
        for i, c in enumerate(cs or []):
            if not isinstance(c, dict):
                continue
            ref = f"data/accelerators/{path.name}#{i}"
            n = (c.get("name") or "").strip() if isinstance(c.get("name"), str) else ""
            if not n:
                skipped.append(ref)
                continue
            st = c.get("status") if isinstance(c.get("status"), str) else None
            exited = bool(c.get("is_exit") is True or (st and any(w in st.lower() for w in ("acquired", "ipo", "exit", "public"))))
            row = {"ref": ref, "type": "accelerator", "backer": an.get(slug, slug), "backer_slug": slug,
                   "name": n, "url": c.get("website") or None, "description": c.get("description") or None,
                   "everywhere_tags": c.get("everywhere_tags") or [], "exited": exited,
                   "location": c.get("location") or None, "stage": c.get("stage") or c.get("round") or None,
                   "first_invested": next((c[k] for k in ACCEL_FIRST if nonempty(c.get(k))), None),
                   "status": st or None, "verticals": c.get("verticals") or None, "team": c.get("team") or None,
                   "linkedin_url": c.get("linkedin_url") or None,
                   "founded": c.get("founded") or c.get("founded_year") or None, "fund": {}, "rel": {}}
            for k, v in c.items():
                if k in ACCEL_IDENTITY or k in FUND_KEYS or k.endswith("_public"):
                    continue
                if nonempty(v):
                    row["rel"][k] = v
            for k in FUND_KEYS:
                for kk in (k, k + "_public"):
                    if kk in c:
                        row["fund"][kk] = c[kk]
            rows.append(row)
    return rows, skipped


def load_records(path):
    recs = {}
    if not path or not os.path.isdir(path):
        return recs
    for f in os.listdir(path):
        if not f.endswith(".json"):
            continue
        try:
            r = json.load(open(os.path.join(path, f), encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        k = r.get("key") or f[:-5]
        recs[k] = r
    return recs


# ---------------- keying ----------------
class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[max(a, b)] = min(a, b)


def regdom(h: str) -> str:
    """Registrable domain: investor.uber.com -> uber.com, shop.aalo.co -> aalo.co, x.co.uk kept."""
    p = h.split(".")
    if len(p) >= 3 and p[-2] in TLD2 and len(p[-1]) == 2:
        return ".".join(p[-3:])
    return ".".join(p[-2:]) if len(p) >= 2 else h


def assign_keys(rows):
    """Sets row['key'] (company id) and row['matched_by']. Returns (possible_matches, shared_hosts)."""
    by_dom = collections.defaultdict(list)
    for i, r in enumerate(rows):
        r["_host"] = domain(r["url"])
        r["_dom"] = regdom(r["_host"]) if host_ok(r["_host"]) else r["_host"]
        r["_nn"] = norm_name(r["name"])
        c = core(r["name"])
        r["_core"] = c if len(c) >= 3 else r["_nn"]
        if host_ok(r["_host"]) and host_ok(r["_dom"]):
            by_dom[r["_dom"]].append(i)
    shared_hosts = {}
    for dom, idxs in by_dom.items():
        lab = host_label(dom)
        cores = sorted({rows[i]["_core"] for i in idxs})
        uf = UF()
        for c in cores:
            uf.find(c)
        if len(cores) > 1:
            for a_i in range(len(cores)):
                for b_i in range(a_i + 1, len(cores)):
                    if compatible(cores[a_i], cores[b_i], lab):
                        uf.union(cores[a_i], cores[b_i])
        clusters = collections.defaultdict(list)
        for i in idxs:
            clusters[uf.find(rows[i]["_core"])].append(i)
        if len(clusters) == 1:
            for i in idxs:
                rows[i]["key"], rows[i]["matched_by"] = dom, "domain"
            continue
        if len(clusters) >= 3:
            shared_hosts[dom] = len(clusters)
        # several unrelated names on one host: only the cluster whose name matches the domain label owns
        # the domain (databricks.com -> Databricks, not an acquired product); the rest fall back to name
        lab_hits = [c for c, ii in clusters.items()
                    if any(matches_label(rows[i]["_core"], lab) or matches_label(rows[i]["_nn"], lab) for i in ii)]
        if len(lab_hits) == 1:
            for i in clusters[lab_hits[0]]:
                rows[i]["key"], rows[i]["matched_by"] = dom, "domain"
    # same distinctive name on several TLDs of the same label (ably.com / ably.io): one company
    groups = collections.defaultdict(set)
    for r in rows:
        if r.get("key") and len(r["_nn"]) >= 7 and r["_nn"] == re.sub(r"[^a-z0-9]", "", label(r["key"])):
            groups[r["_nn"]].add(r["key"])
    alias = {}
    for nn, ks in groups.items():
        if len(ks) > 1:
            cnt = collections.Counter(r["key"] for r in rows if r.get("key") in ks)
            canon = max(sorted(ks), key=lambda k: cnt[k])
            for k in ks:
                if k != canon:
                    alias[k] = canon
    for r in rows:
        if r.get("key") in alias:
            r["domain_alias"] = r["key"]
            r["key"] = alias[r["key"]]
    # name-only rows: join a domain company only if exactly one carries that exact normalized name
    nn_to_keys = collections.defaultdict(set)
    for r in rows:
        if r.get("key"):
            nn_to_keys[r["_nn"]].add(r["key"])
    possible = collections.defaultdict(set)
    for r in rows:
        if r.get("key"):
            continue
        if PLACEHOLDER.match(r["_nn"]):
            # "Stealth" / "Undisclosed" rows are different companies: never merged with each other
            r["key"], r["matched_by"] = "name:" + r["_nn"] + "#" + r["ref"], "placeholder"
            continue
        ks = nn_to_keys.get(r["_nn"], set())
        if len(ks) == 1:
            r["key"], r["matched_by"] = next(iter(ks)), "name"
        else:
            r["key"], r["matched_by"] = "name:" + r["_nn"], "name"
            if len(ks) > 1:
                possible[r["key"]].update(ks)
    # same exact name on different domains (not merged: may be different companies) -> cross-reference
    for nn, ks in nn_to_keys.items():
        if len(ks) > 1:
            for k in ks:
                possible[k].update(ks - {k})
    return {k: sorted(v) for k, v in possible.items()}, shared_hosts


# ---------------- merging ----------------
def _pick(values, prefer_long=False):
    """Most common non-empty value (ties -> longest); returns (best, alternates)."""
    vals = [v.strip() if isinstance(v, str) else v for v in values if nonempty(v)]
    if not vals:
        return None, []
    cnt = collections.Counter(json.dumps(v, ensure_ascii=False, sort_keys=True) for v in vals)
    order = list(dict.fromkeys(json.dumps(v, ensure_ascii=False, sort_keys=True) for v in vals))
    if prefer_long:
        best = max(order, key=lambda s: (len(s), cnt[s]))
    else:
        best = max(order, key=lambda s: (cnt[s], len(s)))
    return json.loads(best), [json.loads(s) for s in order if s != best]


def _split_list(v):
    if isinstance(v, list):
        return [str(x).strip() for x in v if nonempty(x)]
    if isinstance(v, str) and v.strip():
        return [x.strip() for x in re.split(r"[;,|]", v) if x.strip()]
    return []


def build_company(key, rs, recs_for, possible):
    c = {"company_id": key}
    name, alt = _pick([r["name"] for r in rs])
    c["name"] = name
    if alt:
        c["name_alternates"] = alt
    # website: normalize trivial variants away (scheme / www / trailing slash)
    def wnorm(u):
        return re.sub(r"/+$", "", re.sub(r"^https?://(www\.)?", "", u.strip().lower())).strip() if isinstance(u, str) else u
    urls = [r["url"] for r in rs if nonempty(r["url"]) and isinstance(r["url"], str)]
    best, alts = _pick([wnorm(u) for u in urls])
    if best:
        full = next(u for u in urls if wnorm(u) == best)
        c["website"] = full if "//" in full else "https://" + full
        c["domain"] = key if not key.startswith("name:") else None
        alts_full = []
        for a in alts:
            fu = next(u for u in urls if wnorm(u) == a)
            alts_full.append(fu)
        if alts_full:
            c["website_alternates"] = alts_full
    else:
        c["website"] = None
        c["domain"] = None
    d, dalt = _pick([r["description"] for r in rs], prefer_long=True)
    c["description"] = d
    if dalt:
        c["description_alternates"] = dalt
    tags = collections.Counter()
    for r in rs:
        for t in r["everywhere_tags"] if isinstance(r["everywhere_tags"], list) else []:
            if nonempty(t):
                tags[t] += 1
    c["everywhere_tags"] = [t for t, _ in sorted(tags.items(), key=lambda x: (-x[1], str(x[0])))]
    vert = []
    for r in rs:
        for v in _split_list(r.get("verticals")):
            if v not in vert:
                vert.append(v)
    if vert:
        c["verticals"] = vert
    for f in ("location", "status", "founded", "team", "linkedin_url"):
        v, va = _pick([r.get(f) for r in rs], prefer_long=(f in ("location", "team")))
        if v is not None or f in ("location", "status"):
            c[f] = v
        if va:
            c[f + "_alternates"] = va
    c["exited"] = any(r["exited"] for r in rs)
    # relationships
    vcs = list(dict.fromkeys(r["backer"] for r in rs if r["type"] == "vc"))
    acs = list(dict.fromkeys(r["backer"] for r in rs if r["type"] == "accelerator"))
    c["vc_firms"] = vcs
    c["accelerators"] = acs
    c["backer_count"] = len(set((r["type"], r["backer_slug"]) for r in rs))
    backers = []
    for r in sorted(rs, key=lambda r: (r["type"] != "vc", r["backer"].lower(), r["ref"])):
        b = {"type": r["type"], "name": r["backer"], "slug": r["backer_slug"], "source_row": r["ref"],
             "name_on_source": r["name"], "matched_by": r["matched_by"],
             "stage": r["stage"], "first_invested": r["first_invested"], "status": r["status"]}
        if nonempty(r["url"]) and r["url"] != c.get("website"):
            b["url_on_source"] = r["url"]
        if r.get("domain_alias"):
            b["domain_alias"] = r["domain_alias"]
        b.update(r["rel"])
        backers.append(b)
    c["backers"] = backers
    if key in possible:
        c["possible_matches"] = possible[key]
    # transactions
    rounds, grants, urls, notes, firm_rounds, firm_totals = [], [], [], [], [], []
    statuses, checked, stated, inv_rows, scal = [], [], [], [], collections.defaultdict(list)
    sources = [r["fund"] for r in rs] + [{**rec, "_record": True} for rec in recs_for]
    for f in sources:
        if f.get("_record"):
            rr, gg, uu = f.get("rounds") or [], f.get("grants") or [], f.get("urls") or []
            if f.get("status"):
                statuses.append(f["status"])
            if f.get("checked"):
                checked.append(f["checked"])
            if f.get("notes"):
                notes.append(f["notes"])
            if isinstance(f.get("stated_total_raised"), dict):
                stated.append(f["stated_total_raised"])
        else:
            rr = (f.get("funding_rounds") or []) + (f.get("funding_rounds_public") or [])
            gg = (f.get("grants") or []) + (f.get("grants_public") or [])
            uu = (f.get("funding_source_urls") or []) + (f.get("funding_source_urls_public") or [])
            for k in ("funding_status", "funding_status_public"):
                if f.get(k):
                    statuses.append(f[k])
            for k in ("funding_checked", "funding_checked_public"):
                if f.get(k):
                    checked.append(f[k])
            for k in ("funding_notes", "funding_notes_public"):
                if f.get(k):
                    notes.append(f[k])
            for k in ("stated_total_raised", "stated_total_raised_public"):
                if isinstance(f.get(k), dict):
                    stated.append(f[k])
            for k in ("notable_investors", "notable_investors_public"):
                inv_rows += [x for x in (f.get(k) or []) if isinstance(x, str)] if isinstance(f.get(k), list) else []
            for k in FUNDING_SCALARS:
                for kk in (k, k + "_public"):
                    if nonempty(f.get(kk)):
                        scal[k].append(f[kk])
        for x in rr if isinstance(rr, list) else [rr]:
            (rounds if isinstance(x, dict) else firm_rounds).append(x)
        for g in gg if isinstance(gg, list) else []:
            if isinstance(g, dict):
                grants.append(g)
        for u in uu if isinstance(uu, list) else []:
            if isinstance(u, str):
                urls.append(u)
    if not (rounds or grants or urls or statuses or firm_rounds or scal):
        return c
    mr = merge_rounds(rounds)
    gk, mg = set(), []
    for g in grants:
        k = (g.get("name"), g.get("date"))
        if k not in gk:
            gk.add(k)
            mg.append(g)
    st = max(stated, key=lambda s: _num(s.get("amount")) or 0) if stated else None
    out, inv = summarize(mr, st)
    # never lower a stored numeric total; non-numeric firm-site totals are kept as reported
    nums = [v for v in scal.get("total_raised", []) if _num(v) is not None]
    for v in scal.get("total_raised", []):
        if _num(v) is None and v not in firm_totals:
            firm_totals.append(v)
    if nums and (out.get("total_raised") is None or max(nums) > _num(out["total_raised"])):
        out["total_raised"] = max(nums)
        rowcur = [v for v in scal.get("total_raised_currency", []) if isinstance(v, str)]
        out["total_raised_currency"] = rowcur[0] if rowcur else out.get("total_raised_currency")
        out["total_raised_basis"] = (scal.get("total_raised_basis") or ["source_row"])[0]
    for k in FUNDING_SCALARS:
        if k not in out:
            v, _ = _pick([v for v in scal.get(k, []) if not (k == "total_raised" and _num(v) is None)])
            out[k] = v
    c["total_raised"] = out.get("total_raised")
    c["total_raised_currency"] = out.get("total_raised_currency")
    c["total_raised_basis"] = out.get("total_raised_basis")
    if firm_totals:
        c["firm_reported_total_raised"] = firm_totals
    if st:
        c["stated_total_raised"] = st
    c["last_round"] = {"type": out.get("last_round_type"), "amount": out.get("last_round_amount"),
                       "currency": out.get("last_round_currency"), "date": out.get("last_round_date")}
    c["funding_round_count"] = len(mr)
    c["funding_rounds"] = mr
    if firm_rounds:
        c["firm_reported_rounds"] = list(dict.fromkeys(json.dumps(x, ensure_ascii=False) for x in firm_rounds))
        c["firm_reported_rounds"] = [json.loads(x) for x in c["firm_reported_rounds"]]
    if mg:
        c["grants"] = mg
    allinv = list(dict.fromkeys(inv + inv_rows))
    if allinv:
        c["notable_investors"] = allinv
    su = [u for u in dict.fromkeys(urls + [r.get("source_url") for r in mr + mg if r.get("source_url")]) if u and not banned(u)]
    if su:
        c["funding_source_urls"] = su
    ss = [s for s in statuses if s in STATUS_ORDER]
    c["funding_status"] = max(ss, key=STATUS_ORDER.index) if ss else (statuses[0] if statuses else None)
    c["funding_checked"] = max(str(x) for x in checked) if checked else None
    nn = list(dict.fromkeys(n for n in notes if isinstance(n, str)))
    if nn:
        c["funding_notes"] = nn
    return c


def records_for_rows(rows, recs):
    """company key -> research records that apply (same matching as funding_all/apply.py)."""
    out = collections.defaultdict(dict)
    if not recs:
        return out
    for r in rows:
        d = r["_host"]
        if d and d not in recs and r["_dom"] in recs:
            d = r["_dom"]
        if d and d in recs:
            rec = recs[d]
            # only the company that owns the domain, or a row whose name agrees with the record
            if r["matched_by"] == "domain" or compatible(core(rec.get("name")), r["_core"], label(d)):
                out[r["key"]][d] = rec
        nk = "name:" + core(r["name"])
        if nk in recs and (not d or not host_ok(d) or r["key"].startswith("name:") or r["matched_by"] == "name"):
            out[r["key"]][nk] = recs[nk]
    return out


# ---------------- output ----------------
def _dumps(rows):
    return json.dumps(rows, indent=1, ensure_ascii=False) + "\n"


def part_filename(i):
    return f"{OUT_BASE}.json" if i == 0 else f"{OUT_BASE}_{i + 1}.json"


def split_parts(companies, limit=PART_LIMIT_BYTES):
    parts, cur, cur_b = [], [], 4
    for c in companies:
        t = json.dumps(c, indent=1, ensure_ascii=False)
        b = len(t.encode("utf-8")) + (t.count("\n") + 1) + 2
        if cur and cur_b + b > limit:
            parts.append(cur)
            cur, cur_b = [], 4
        cur.append(c)
        cur_b += b
    if cur or not parts:
        parts.append(cur)
    return parts


def build(records_dir=DEFAULT_RECORDS):
    rows, skipped = load_rows()
    possible, shared = assign_keys(rows)
    recs = load_records(records_dir)
    rec_map = records_for_rows(rows, recs)
    groups = collections.defaultdict(list)
    for r in rows:
        groups[r["key"]].append(r)
    companies = [build_company(k, rs, list(rec_map.get(k, {}).values()), possible) for k, rs in groups.items()]
    companies.sort(key=lambda c: ((c["name"] or "").lower(), c["company_id"]))
    return rows, skipped, companies, shared, recs


def validate(rows, companies):
    seen = collections.Counter()
    for c in companies:
        for b in c["backers"]:
            seen[b["source_row"]] += 1
    refs = [r["ref"] for r in rows]
    assert len(refs) == len(set(refs)), "duplicate source refs"
    missing = [x for x in refs if seen[x] == 0]
    dup = [x for x, n in seen.items() if n > 1]
    extra = set(seen) - set(refs)
    assert not missing, f"{len(missing)} source rows not mapped, e.g. {missing[:5]}"
    assert not dup, f"{len(dup)} source rows mapped twice, e.g. {dup[:5]}"
    assert not extra, f"{len(extra)} unknown refs"
    assert sum(seen.values()) == len(rows)
    assert len({c["company_id"] for c in companies}) == len(companies), "duplicate company ids"
    return True


def stats(rows, companies, skipped, shared, recs):
    multi = sum(1 for c in companies if c["backer_count"] >= 2)
    return {
        "total_source_rows": len(rows),
        "vc_source_rows": sum(1 for r in rows if r["type"] == "vc"),
        "accelerator_source_rows": sum(1 for r in rows if r["type"] == "accelerator"),
        "unnamed_source_rows_skipped": len(skipped),
        "unique_companies": len(companies),
        "companies_with_2plus_backers": multi,
        "companies_with_vc_and_accelerator": sum(1 for c in companies if c["vc_firms"] and c["accelerators"]),
        "companies_keyed_by_domain": sum(1 for c in companies if not c["company_id"].startswith("name:")),
        "companies_keyed_by_name": sum(1 for c in companies if c["company_id"].startswith("name:")),
        "name_rows_joined_to_domain_company": sum(1 for r in rows if r["matched_by"] == "name" and not r["key"].startswith("name:")),
        "companies_with_possible_matches": sum(1 for c in companies if c.get("possible_matches")),
        "shared_hosts_treated_as_junk": len(shared),
        "companies_with_funding_rounds": sum(1 for c in companies if c.get("funding_rounds")),
        "companies_funding_checked": sum(1 for c in companies if c.get("funding_checked")),
        "funding_rounds_total": sum(len(c.get("funding_rounds") or []) for c in companies),
        "research_records_available": len(recs),
    }


def write(companies, st, data_dir=DATA):
    parts = split_parts(companies)
    entries = []
    for i, p in enumerate(parts):
        txt = _dumps(p)
        (data_dir / part_filename(i)).write_text(txt, encoding="utf-8")
        entries.append({"file": part_filename(i), "companies": len(p), "bytes": len(txt.encode("utf-8")),
                        "first_company": p[0]["name"] if p else None, "last_company": p[-1]["name"] if p else None})
    keep = {part_filename(i) for i in range(len(parts))}
    for f in data_dir.glob(f"{OUT_BASE}*.json"):
        if _PART_RE.match(f.name) and f.name not in keep:
            f.unlink()
    idx = {"_comment": "One row per unique company across every Private Comps firm file and accelerator file "
                       "(core identity + every backing firm/accelerator + all funding rounds). Split into parts of "
                       "<= ~40 MB; concatenate every part in order. Built by automation/unique_builder.py; the "
                       "per-firm master (all_companies*.json) and every firm/accelerator file are unchanged.",
           "part_limit_bytes": PART_LIMIT_BYTES, **st, "parts": entries}
    (data_dir / INDEX_FILENAME).write_text(json.dumps(idx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return idx


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--records", default=DEFAULT_RECORDS, help="funding research records dir ('' to skip)")
    ap.add_argument("--check", action="store_true", help="validate + print stats, write nothing")
    a = ap.parse_args()
    rows, skipped, companies, shared, recs = build(a.records)
    validate(rows, companies)
    st = stats(rows, companies, skipped, shared, recs)
    print(json.dumps(st, indent=2))
    if a.check:
        return 0
    idx = write(companies, st)
    for e in idx["parts"]:
        print(f"[unique_builder] wrote data/{e['file']}: {e['companies']} companies, {e['bytes']:,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
