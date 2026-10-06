"""Rebuild data/accelerators/all_accelerator_companies.json from every
{slug}_companies.json (hax/indiebio are subsets of sosv and are skipped)."""
import glob
import json
import os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "accelerators")
SUBSETS = {"hax", "indiebio"}
out, counts = [], {}
for f in sorted(glob.glob(os.path.join(DATA, "*_companies.json"))):
    slug = os.path.basename(f)[:-len("_companies.json")]
    if slug in SUBSETS or slug == "all_accelerator":
        continue
    cs = json.load(open(f))["companies"]
    counts[slug] = len(cs)
    out += [{"accelerator": slug, **c} for c in cs]
json.dump({"count": len(out), "by_accelerator": counts, "companies": out},
          open(os.path.join(DATA, "all_accelerator_companies.json"), "w"), ensure_ascii=False)
print(len(out), counts)
