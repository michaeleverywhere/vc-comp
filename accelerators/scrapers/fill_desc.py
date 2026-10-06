"""Fill blank descriptions from each company's own website (meta/og description),
for an existing data/accelerators/{slug}_companies.json. Never touches banned sources."""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
from common import DATA_DIR, site_info, tag
for slug in sys.argv[1:]:
    p = os.path.join(DATA_DIR, f"{slug}_companies.json")
    d = json.load(open(p))
    R = d["companies"] if isinstance(d, dict) else d
    todo = [r for r in R if not r.get("description") and r.get("website")]
    with ThreadPoolExecutor(16) as ex:
        res = list(ex.map(lambda r: site_info(r["website"], name=r.get("name")), todo))
    n = 0
    for r, (desc, li) in zip(todo, res):
        if desc:
            r["description"] = desc
            r["description_source"] = "company website meta description"
            if not r.get("everywhere_tags"):
                r["everywhere_tags"] = tag(r["name"], desc, [x for x in (r.get("verticals") or "").split("; ") if x])
            n += 1
        if li and not r.get("linkedin_url"):
            r["linkedin_url"] = li
            r["linkedin_source"] = "company website"
    json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
    print(slug, "missing", len(todo) + sum(1 for r in R if not r.get("description") and not r.get("website")) , "filled", n,
          "still blank", sum(1 for r in R if not r.get("description")), flush=True)
