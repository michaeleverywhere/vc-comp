"""SOSV refresh: re-pull the public WordPress REST API (sosv.py: sosv.com + hax.co) and merge
onto the existing data/accelerators/sosv_companies.json, then rewrite the hax_/indiebio_ subsets.

Fresh SOSV values win; fields SOSV now leaves blank keep the earlier value (company-site
LinkedIn/descriptions, tags, funding fields). Renames (same cohort + same website/description)
keep their record and get `former_name`. Company-site enrichment only runs for new rows.
Afterwards run add_batch_fields.py sosv hax indiebio and build_combined.py.
"""
import json
import os

import sosv
from common import DATA_DIR, enrich_from_sites, norm_name, save

PATH = os.path.join(DATA_DIR, "sosv_companies.json")
RECOMPUTED = ("batch_date", "batch_date_precision", "most_recent_batch")


def main():
    cap = {}
    sosv.save = lambda slug, recs, meta=None: cap.setdefault(slug, (recs, meta))
    sosv.enrich_from_sites = lambda recs, **k: 0
    sosv.main()
    fresh, meta = cap["sosv"]
    old = json.load(open(PATH))["companies"]
    O = {norm_name(r["name"]): r for r in old}
    fresh_keys = {norm_name(r["name"]) for r in fresh}
    orphans = [r for k, r in O.items() if k not in fresh_keys]
    added, renamed, changed, out = [], [], {}, []
    for r in fresh:
        o = O.get(norm_name(r["name"]))
        if o is None:
            for c in orphans:
                if c.get("date") == r.get("date") and (
                        (c.get("description") and c.get("description") == r.get("description"))
                        or (c.get("website") and c.get("website") == r.get("website"))):
                    o = c
                    orphans.remove(c)
                    r["former_name"] = c["name"]
                    renamed.append((c["name"], r["name"]))
                    break
        if o is None:
            added.append(r)
        else:
            for f, v in o.items():
                if f in RECOMPUTED:
                    continue
                if v not in ("", None, []) and r.get(f) in ("", None, []):
                    r[f] = v
                elif r.get(f) != v and f not in ("linkedin_source", "description_source"):
                    changed.setdefault(f, []).append(r["name"])
            if o.get("description_source") and r.get("description") != o.get("description"):
                r.pop("description_source", None)
            for f in RECOMPUTED:   # keep until add_batch_fields recomputes
                if f in o:
                    r[f] = o[f]
        out.append(r)
    enrich_from_sites(added)
    meta = dict(meta or {}, hax_only_added=sum(1 for r in out if r.get("site") == "hax.co"))
    save("sosv", out, meta)
    save("hax", [r for r in out if r["investors"] == "SOSV (HAX)"],
         {"note": "subset of sosv_companies.json; Airtable rows come from SOSV set"})
    save("indiebio", [r for r in out if r["investors"] == "SOSV (IndieBio)"],
         {"note": "subset of sosv_companies.json; IndieBio = SOSV NY/SF since 2024"})
    json.dump({"added": [(r["name"], r.get("date"), r["investors"]) for r in added],
               "renamed": renamed, "dropped": [(c["name"], c.get("date")) for c in orphans],
               "changed": changed}, open("/tmp/sosv_refresh_report.json", "w"), indent=1)
    print(f"[sosv_refresh] before {len(old)} after {len(out)} added {[r['name'] for r in added]} "
          f"renamed {renamed} dropped {[c['name'] for c in orphans]}")
    print({f: len(v) for f, v in changed.items()})


if __name__ == "__main__":
    main()
