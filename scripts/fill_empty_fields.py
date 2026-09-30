#!/usr/bin/env python3
"""
Fill empty Private Comps company fields from EXISTING firm-site scrape data only.

Rules (never invent):
  - Only fill a field if the record already defines that key (site-tailored schemas).
  - Sources: other fields on the same record (tagline→description, acquirer→status,
    clear name/description exit phrases → status, status synonym normalize).
  - Does NOT touch LAST FINANCING / TOTAL RAISED / ARR / VALUATION / TEAM SIZE / TRACKED BY.
  - Does NOT call Crunchbase / LinkedIn / PitchBook.

Writes provenance to artifacts/field_fill_report.json
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
ART = Path(__file__).resolve().parent.parent / "artifacts"
ART.mkdir(exist_ok=True)

ACQUIRED_STATUS = "acquired"
ACTIVE_STATUS = "active"
LIVE_STATUS = "live"

# Clear synonym → canonical (only active|live|acquired)
STATUS_MAP = {
    "active": ACTIVE_STATUS,
    "current": ACTIVE_STATUS,
    "current investment": ACTIVE_STATUS,
    "live": LIVE_STATUS,
    "acquired": ACQUIRED_STATUS,
    "acquisition": ACQUIRED_STATUS,
    "exited": ACQUIRED_STATUS,
    "exit": ACQUIRED_STATUS,
    "m&a": ACQUIRED_STATUS,
    "merged": ACQUIRED_STATUS,
    "aquired": ACQUIRED_STATUS,  # typo
}

# Patterns that clearly imply acquired (applied to status string / name / desc)
ACQUIRED_IN_STATUS = re.compile(
    r"(?i)\b(acquired|acquisition|merged with|sold to)\b"
)
TICKER_ACQUIRED = re.compile(r"(?i)acquired by")
NAME_EXIT = re.compile(r"\((?i:Acquired|Exited|Merged)[^)]*\)")
DESC_ACQUIRED = re.compile(
    r"(?i)\b(?:was\s+)?acquired by\b|\bmerged with\b|\bacquisition by\b"
)


def nonempty(v) -> bool:
    if v is None:
        return False
    if isinstance(v, bool):
        return True
    if isinstance(v, (int, float)):
        return True
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, dict)):
        return len(v) > 0
    return bool(v)


def dataset_files():
    files = sorted(DATA.glob("*_companies.json"))
    files = [p for p in files if p.name != "all_companies.json"]
    if (DATA / "companies.json").exists():
        files.append(DATA / "companies.json")
    return files


def normalize_status(raw: str) -> str | None:
    """Return canonical active|live|acquired if clear, else None (leave as-is)."""
    s = (raw or "").strip()
    if not s:
        return None
    low = s.lower().strip()
    if low in STATUS_MAP:
        return STATUS_MAP[low]
    if ACQUIRED_IN_STATUS.search(s) or TICKER_ACQUIRED.search(s):
        return ACQUIRED_STATUS
    # Explicit public/IPO alone is NOT active|live|acquired — leave unchanged
    return None


def derive_status(o: dict) -> str | None:
    """Derive status only when the record already has a status key that is empty."""
    if "status" not in o or nonempty(o.get("status")):
        return None
    if o.get("acquirer"):
        return ACQUIRED_STATUS
    et = o.get("exit_type")
    if isinstance(et, str) and et.strip():
        low = et.lower()
        if any(w in low for w in ("acquir", "merger", "merged", "exit")):
            return ACQUIRED_STATUS
    if o.get("is_acquired") is True:
        return ACQUIRED_STATUS
    name = o.get("company_name") or o.get("name") or ""
    if NAME_EXIT.search(name):
        return ACQUIRED_STATUS
    desc = o.get("description") or ""
    if DESC_ACQUIRED.search(desc):
        return ACQUIRED_STATUS
    # Clear active signals
    if o.get("is_current_investment") is True or o.get("is_active") is True:
        return ACTIVE_STATUS
    return None


def main():
    report = {
        "tagline_to_description": [],
        "status_normalized": [],
        "status_derived": [],
        "counts": Counter(),
    }

    for path in dataset_files():
        data = json.load(open(path))
        changed = False
        for o in data:
            cname = o.get("company_name") or o.get("name") or "?"

            # 1) tagline → empty description (same record, already-scraped)
            if "description" in o and not nonempty(o.get("description")):
                tag = o.get("tagline")
                if nonempty(tag) and isinstance(tag, str):
                    o["description"] = tag.strip()
                    changed = True
                    report["tagline_to_description"].append(
                        {"file": path.name, "company": cname, "value": o["description"][:120]}
                    )
                    report["counts"]["tagline_to_description"] += 1

            # 2) normalize existing non-empty status when clearly mappable
            if "status" in o and isinstance(o.get("status"), str) and o["status"].strip():
                canon = normalize_status(o["status"])
                if canon and canon != o["status"]:
                    old = o["status"]
                    o["status"] = canon
                    changed = True
                    report["status_normalized"].append(
                        {"file": path.name, "company": cname, "from": old, "to": canon}
                    )
                    report["counts"]["status_normalized"] += 1

            # 3) derive empty status from other existing fields
            derived = derive_status(o)
            if derived:
                o["status"] = derived
                changed = True
                report["status_derived"].append(
                    {"file": path.name, "company": cname, "value": derived}
                )
                report["counts"]["status_derived"] += 1

        if changed:
            json.dump(data, open(path, "w"), ensure_ascii=False, indent=2)
            print(f"updated {path.name}")

    # serialize Counter
    report["counts"] = dict(report["counts"])
    # keep report compact: truncate long lists
    for k in ("tagline_to_description", "status_normalized", "status_derived"):
        report[f"{k}_count"] = len(report[k])
        report[k] = report[k][:200]  # sample

    out = ART / "field_fill_report.json"
    json.dump(report, open(out, "w"), ensure_ascii=False, indent=2)
    print(f"\ncounts: {report['counts']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
