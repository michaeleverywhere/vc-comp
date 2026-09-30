#!/usr/bin/env python3
"""Focused Wikidata backfill of empty location/headquarters only.
Reuses enrich.py helpers; fills ONLY empty location fields; never invents.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enrich as E

LOC_KEYS = ("location", "headquarters")
FILES = [
    "accel_companies.json", "insight_companies.json", "felicis_companies.json",
    "rre_companies.json", "eclipseventures_companies.json", "greylock_companies.json",
    "draperassociates_companies.json", "arch_companies.json", "eniacventures_companies.json",
    "balderton_companies.json", "lowercarbon_companies.json", "hustlefund_companies.json",
]

def empty(v):
    if v is None: return True
    if isinstance(v, str): return not v.strip()
    if isinstance(v, list): return len(v)==0
    return False

def main():
    report = []
    for fname in FILES:
        path = os.path.join(E.DATA_DIR, fname)
        if not os.path.exists(path):
            print(f"skip missing {fname}")
            continue
        data = json.load(open(path))
        pending = []
        label_ids = []
        for o in data:
            loc_key = next((k for k in LOC_KEYS if k in o), None)
            if not loc_key or not empty(o.get(loc_key)):
                continue
            dom = E.domain_of(o.get("company_url"))
            if not dom:
                continue
            name = o.get("company_name") or o.get("name")
            if not name:
                continue
            qid, claims = E.wd_match(name, dom)
            time.sleep(0.08)
            if not qid:
                continue
            hq = E.ent_ids(claims, "P159")
            if not hq:
                continue
            pending.append((o, fname, qid, loc_key, hq))
            label_ids += hq
        labels = E.get_labels(label_ids)
        n = 0
        for o, fname, qid, loc_key, hq in pending:
            places = []
            for q in hq:
                lab = labels.get(q)
                if lab and lab not in places:
                    places.append(lab)
            if places:
                o[loc_key] = ", ".join(places)
                n += 1
                report.append({"file": fname, "company": o.get("company_name"),
                               "source": "wikidata", "wikidata_id": qid,
                               "filled": {loc_key: o[loc_key]}})
        json.dump(data, open(path, "w"), ensure_ascii=False, indent=2)
        print(f"{fname}: filled {n} locations", flush=True)

    # merge into enrichment_report
    report_path = os.path.join(E.DATA_DIR, "enrichment_report.json")
    existing = []
    if os.path.exists(report_path):
        try:
            existing = json.load(open(report_path))
        except Exception:
            existing = []
    # drop prior location fills for these files from this script's scope, keep rest
    loc_files = set(FILES)
    kept = [r for r in existing if not (
        r.get("file") in loc_files and isinstance(r.get("filled"), dict)
        and any(k in r["filled"] for k in LOC_KEYS)
    )]
    json.dump(kept + report, open(report_path, "w"), ensure_ascii=False, indent=2)
    print(f"TOTAL location fills: {len(report)}", flush=True)

if __name__ == "__main__":
    main()
