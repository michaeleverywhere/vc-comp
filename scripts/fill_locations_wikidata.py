#!/usr/bin/env python3
"""Fill empty location from Wikidata P159, domain-verified only.

Never overwrites a non-empty location/headquarters. Does not use
Crunchbase, LinkedIn, or PitchBook. Caches lookups so a rerun is cheap.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enrich as E

E.HEADERS = {
    "User-Agent": (
        "vc-comps-location/1.0 (+https://github.com/michaeleverywhere/vc-comp; "
        "portfolio location backfill)"
    )
}

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)
CACHE_PATH = ART / "wd_location_cache.json"

LOC_KEYS = ("location", "headquarters", "hq", "hq_location", "city", "country")

_rate_lock = threading.Lock()
_next_at = 0.0
_orig_api = E.api


def _api(params):
    global _next_at
    with _rate_lock:
        now = time.time()
        if now < _next_at:
            time.sleep(_next_at - now)
        _next_at = time.time() + 0.15
    return _orig_api(params)


E.api = _api


def nonempty(v) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, dict)):
        return len(v) > 0
    return bool(v)


def has_loc(rec: dict) -> bool:
    return any(nonempty(rec.get(k)) for k in LOC_KEYS)


def dataset_files():
    files = sorted(DATA.glob("*_companies.json"))
    files = [p for p in files if p.name != "all_companies.json"]
    extra = DATA / "companies.json"
    if extra.exists():
        files.append(extra)
    return files


def load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def main():
    cache = load_cache()
    work = []  # (name, domain)
    seen = set()
    for path in dataset_files():
        data = json.loads(path.read_text())
        if not isinstance(data, list):
            continue
        for rec in data:
            if has_loc(rec):
                continue
            url = rec.get("company_url") or rec.get("url") or rec.get("website")
            dom = E.domain_of(url) if isinstance(url, str) else None
            name = rec.get("company_name") or rec.get("name")
            if not dom or not name:
                continue
            key = f"{name.strip().lower()}|{dom}"
            if key in seen:
                continue
            seen.add(key)
            if key not in cache:
                work.append((key, name, dom))

    print(f"cache={len(cache)} to_lookup={len(work)} unique_missing={len(seen)}", flush=True)

    lock = threading.Lock()
    done = {"n": 0, "hit": 0}

    def lookup(item):
        key, name, dom = item
        try:
            qid, claims = E.wd_match(name, dom)
            place = None
            if qid and claims:
                hq = E.ent_ids(claims, "P159")
                labels = E.get_labels(hq) if hq else {}
                places = []
                for q in hq:
                    lab = labels.get(q)
                    if lab and lab not in places:
                        places.append(lab)
                if places:
                    place = ", ".join(places)
            return key, {"qid": qid, "location": place}
        except Exception as e:  # noqa: BLE001
            return key, {"qid": None, "location": None, "error": type(e).__name__}

    from concurrent.futures import ThreadPoolExecutor, as_completed

    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(lookup, w) for w in work]
        for fut in as_completed(futs):
            key, val = fut.result()
            with lock:
                cache[key] = val
                done["n"] += 1
                if val.get("location"):
                    done["hit"] += 1
                if done["n"] % 100 == 0:
                    CACHE_PATH.write_text(json.dumps(cache))
                    print(
                        f"  looked {done['n']}/{len(work)} hits={done['hit']}",
                        flush=True,
                    )

    CACHE_PATH.write_text(json.dumps(cache))

    filled = 0
    for path in dataset_files():
        data = json.loads(path.read_text())
        if not isinstance(data, list):
            continue
        changed = False
        for rec in data:
            if has_loc(rec):
                continue
            url = rec.get("company_url") or rec.get("url") or rec.get("website")
            dom = E.domain_of(url) if isinstance(url, str) else None
            name = rec.get("company_name") or rec.get("name")
            if not dom or not name:
                continue
            key = f"{name.strip().lower()}|{dom}"
            loc = (cache.get(key) or {}).get("location")
            if not loc:
                continue
            # Prefer an existing empty location key; otherwise introduce location.
            wrote = False
            for k in ("location", "headquarters", "hq", "hq_location"):
                if k in rec and not nonempty(rec.get(k)):
                    rec[k] = loc
                    wrote = True
                    break
            if not wrote:
                rec["location"] = loc
            filled += 1
            changed = True
        if changed:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            print(f"updated {path.name}", flush=True)

    print(f"FILLED {filled} lookups={done['n']} cache_hits_in_run={done['hit']}", flush=True)


if __name__ == "__main__":
    main()
