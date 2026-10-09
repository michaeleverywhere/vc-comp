"""Techstars refresh: re-pull the public Typesense index (techstars.py) and merge onto the
existing data/accelerators/techstars_companies.json.

Fresh Techstars values win; fields Techstars now leaves blank keep the earlier value
(company-site descriptions / LinkedIn, websites, tags, any funding fields). Companies that
Techstars renamed (same program/year + same description or website) keep their record and
get `former_name`. Afterwards run add_batch_fields.py techstars.
"""
import json
import os

import techstars
from common import DATA_DIR, norm_name, save

PATH = os.path.join(DATA_DIR, "techstars_companies.json")


def main():
    cap = {}
    techstars.save = lambda slug, recs, meta=None: cap.update(recs=recs, meta=meta)
    techstars.main()
    fresh = cap["recs"]
    old = json.load(open(PATH))["companies"]
    O = {norm_name(r["name"]): r for r in old}
    fresh_keys = {norm_name(r["name"]) for r in fresh}
    orphans = [r for k, r in O.items() if k not in fresh_keys]
    added, renamed, out = [], [], []
    for r in fresh:
        k = norm_name(r["name"])
        o = O.get(k)
        if o is None:   # renamed in Techstars' index? same cohort + same description/website
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
            added.append(r["name"])
        else:
            for f, v in o.items():
                if f in ("batch_date", "batch_date_precision", "most_recent_batch"):
                    continue    # recomputed by add_batch_fields.py
                if v not in ("", None, []) and r.get(f) in ("", None, []):
                    r[f] = v
            if o.get("description_source") and r.get("description") != o.get("description"):
                r.pop("description_source", None)   # Techstars now publishes its own text
        out.append(r)
    save("techstars", out, cap["meta"])
    print(f"[techstars_refresh] before {len(old)} after {len(out)} added {added} renamed {renamed} "
          f"dropped {[c['name'] for c in orphans]}")


if __name__ == "__main__":
    main()
