"""Small shared tail for Daily 20 scrapers (write + coverage print)."""
import json


def write_out(out, path, keys):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {path}")
    for k in keys:
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")
