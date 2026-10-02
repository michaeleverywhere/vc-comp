#!/usr/bin/env python3
"""
Backfill empty company_name / description from firm-site re-scrapes only.

- Inventories empties across data/*_companies.json (excl. all_companies.json)
- Re-runs each firm's scraper into artifacts/rescrape_tmp/
- Merges ONLY into empty company_name / description on existing records
- Never invents; never touches non-empty fields; no third-party DBs
- Writes artifacts/backfill_name_desc_report.json
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SCRIPTS = ROOT / "scripts"
ART = ROOT / "artifacts"
TMP = ART / "rescrape_tmp"
TMP.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "automation"))
import identity  # noqa: E402


def empty(v) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    return False


def dataset_files():
    files = sorted(DATA.glob("*_companies.json"))
    return [p for p in files if p.name != "all_companies.json"]


def inventory():
    by_firm_name = Counter()
    by_firm_desc = Counter()
    firm_totals = {}
    miss_name = miss_desc = total = 0
    for p in dataset_files():
        data = json.load(open(p))
        slug = identity.slug_from_file(p.name) or p.stem
        firm_totals[slug] = len(data)
        for o in data:
            total += 1
            name = identity.company_name(o)
            if empty(name):
                miss_name += 1
                by_firm_name[slug] += 1
            desc = o.get("description") if "description" in o else None
            # Count missing when key absent OR empty
            if "description" not in o or empty(o.get("description")):
                miss_desc += 1
                by_firm_desc[slug] += 1
    return {
        "total": total,
        "miss_name": miss_name,
        "miss_desc": miss_desc,
        "cov_name": (total - miss_name) / total if total else 0,
        "cov_desc": (total - miss_desc) / total if total else 0,
        "by_firm_name": dict(by_firm_name),
        "by_firm_desc": dict(by_firm_desc),
        "firm_totals": firm_totals,
    }


def load_scraper(slug: str):
    path = SCRIPTS / f"{slug}_scraper.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"scraper_{slug}", path)
    mod = importlib.util.module_from_spec(spec)
    # Ensure scraper can import _scraper_common / tags
    sys.path.insert(0, str(SCRIPTS))
    sys.path.insert(0, str(ROOT / "automation"))
    spec.loader.exec_module(mod)
    return mod


def run_scraper_to_tmp(slug: str, limit: int | None = None) -> Path | None:
    mod = load_scraper(slug)
    if mod is None or not hasattr(mod, "main"):
        return None
    out = TMP / f"{slug}_companies.json"
    if hasattr(mod, "OUT"):
        mod.OUT = str(out)
    # Some scrapers use different out var names
    for attr in ("OUT", "OUTPUT", "OUT_PATH", "DATA_PATH"):
        if hasattr(mod, attr):
            setattr(mod, attr, str(out))
    argv = [f"{slug}_scraper.py"]
    if limit is not None:
        argv += ["--limit", str(limit)]
    old_argv = sys.argv
    sys.argv = argv
    try:
        mod.main()
    finally:
        sys.argv = old_argv
    if not out.exists():
        # Scraper may have written to hardcoded relative path despite patch —
        # check data/ and move if scraped_at is brand new (risky). Prefer fail.
        return None
    return out


def match_key(rec: dict) -> str:
    return identity.company_key(rec) or (identity.company_name(rec) or "").strip().lower()


def merge_empty_fields(existing: list[dict], fresh: list[dict]) -> tuple[list[dict], list[dict]]:
    """Fill only empty company_name / description on existing from fresh. Returns (updated, fills)."""
    fresh_by = {}
    for r in fresh:
        k = match_key(r)
        if k and k not in fresh_by:
            fresh_by[k] = r
    # also index by normalized name
    fresh_by_name = {}
    for r in fresh:
        n = (identity.company_name(r) or "").strip().lower()
        if n and n not in fresh_by_name:
            fresh_by_name[n] = r

    fills = []
    for o in existing:
        k = match_key(o)
        n = (identity.company_name(o) or "").strip().lower()
        src = fresh_by.get(k) or fresh_by_name.get(n)
        if not src:
            continue
        # company_name
        if empty(o.get("company_name")) and not empty(src.get("company_name")):
            o["company_name"] = src["company_name"].strip()
            fills.append({"field": "company_name", "company": o["company_name"], "value": o["company_name"]})
        # description: only if key exists on existing (site-tailored) OR we already have description key
        if "description" in o and empty(o.get("description")):
            new_d = src.get("description")
            if not empty(new_d) and isinstance(new_d, str):
                o["description"] = new_d.strip()
                fills.append(
                    {
                        "field": "description",
                        "company": identity.company_name(o),
                        "value": o["description"][:160],
                    }
                )
    return existing, fills


def firms_needing_rescrape(inv) -> list[str]:
    """Firms with any missing name or description."""
    slugs = set(inv["by_firm_name"]) | set(inv["by_firm_desc"])
    return sorted(slugs)


def main():
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1].split(",")
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    dry = "--dry-run" in sys.argv
    skip_rescrape = "--merge-only" in sys.argv  # use existing tmp files

    before = inventory()
    print(
        f"BEFORE total={before['total']} name_cov={before['cov_name']*100:.2f}% "
        f"desc_cov={before['cov_desc']*100:.2f}% miss_name={before['miss_name']} miss_desc={before['miss_desc']}"
    )

    targets = firms_needing_rescrape(before)
    if only:
        targets = [t for t in targets if t in only]
    print(f"targets ({len(targets)}): {targets}")

    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "before": before,
        "rescrape": {},
        "fills_by_firm": {},
        "fills": [],
        "errors": [],
    }

    for slug in targets:
        print(f"\n=== {slug} ===")
        tmp_path = TMP / f"{slug}_companies.json"
        try:
            if not skip_rescrape:
                print(f"  rescraping -> {tmp_path}")
                got = run_scraper_to_tmp(slug, limit=limit)
                if got is None:
                    # fallback: some scrapers ignore OUT patch and write to data/
                    # detect by comparing - we do NOT want that. Record error.
                    report["errors"].append({"slug": slug, "error": "scraper did not write to tmp (OUT patch missed)"})
                    print("  ERROR: no tmp output")
                    continue
            if not tmp_path.exists():
                report["errors"].append({"slug": slug, "error": "tmp missing"})
                continue
            fresh = json.load(open(tmp_path))
            if not isinstance(fresh, list):
                report["errors"].append({"slug": slug, "error": "tmp not a list"})
                continue
            firm_path = DATA / identity.data_file_for(slug)
            if not firm_path.exists():
                report["errors"].append({"slug": slug, "error": f"missing {firm_path.name}"})
                continue
            existing = json.load(open(firm_path))
            n_empty_before = sum(
                1 for o in existing if "description" in o and empty(o.get("description"))
            ) + sum(1 for o in existing if "description" not in o)
            existing2, fills = merge_empty_fields(existing, fresh)
            fresh_desc = sum(1 for o in fresh if not empty(o.get("description")))
            report["rescrape"][slug] = {
                "fresh_n": len(fresh),
                "fresh_with_desc": fresh_desc,
                "empty_desc_before": n_empty_before,
                "fills": len(fills),
            }
            report["fills_by_firm"][slug] = len(fills)
            for f in fills:
                f["firm"] = slug
                report["fills"].append(f)
            print(f"  fresh={len(fresh)} with_desc={fresh_desc} fills={len(fills)}")
            if fills and not dry:
                with open(firm_path, "w", encoding="utf-8") as fh:
                    json.dump(existing2, fh, ensure_ascii=False, indent=2)
                    fh.write("\n")
                print(f"  wrote {firm_path.name}")
        except SystemExit as e:
            report["errors"].append({"slug": slug, "error": f"SystemExit: {e}"})
            print(f"  SystemExit: {e}")
        except Exception as e:
            report["errors"].append({"slug": slug, "error": str(e), "trace": traceback.format_exc()[-500:]})
            print(f"  ERROR: {e}")

    after = inventory()
    report["after"] = after
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["delta_name_filled"] = before["miss_name"] - after["miss_name"]
    report["delta_desc_filled"] = before["miss_desc"] - after["miss_desc"]

    out_path = ART / "backfill_name_desc_report.json"
    # make JSON-serializable (Counters already dicts)
    json.dump(report, open(out_path, "w"), indent=2)
    print(
        f"\nAFTER name_cov={after['cov_name']*100:.2f}% desc_cov={after['cov_desc']*100:.2f}% "
        f"Δname={report['delta_name_filled']} Δdesc={report['delta_desc_filled']}"
    )
    print(f"report -> {out_path}")
    print(f"errors: {len(report['errors'])}")


if __name__ == "__main__":
    main()
