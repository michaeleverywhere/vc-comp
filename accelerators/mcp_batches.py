"""Write 50-row create_records_for_table batches (field IDs) for one accelerator,
skipping Name+Investors pairs already in Airtable (names listed in --existing file)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from airtable_rows import rows, by_id
slug, outdir = sys.argv[1], sys.argv[2]
ex = set()
if len(sys.argv) > 3 and os.path.exists(sys.argv[3]):
    ex = {l.strip().lower() for l in open(sys.argv[3]) if l.strip()}
rs = [r for r in rows(slug) if r["Name"].strip().lower() not in ex]
os.makedirs(outdir, exist_ok=True)
n = 0
for i in range(0, len(rs), 50):
    json.dump([{"fields": by_id(r)} for r in rs[i:i + 50]],
              open(f"{outdir}/{slug}_{i // 50:03d}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    n += 1
print(slug, len(rs), "rows", n, "batches")
