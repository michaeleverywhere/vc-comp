"""Builds data/all_companies.json — every firm's dataset combined into one file,
each record tagged with which firm it came from and normalized through identity.py's
field-alias rules (site-tailored schemas mean "company name" comes in under a dozen
different keys across the 61+ bespoke scrapers; identity.py already solves this, this
module just applies it once across every dataset instead of once per firm).

Pure/offline: build() only reads local files, no network or GitHub calls. The pipeline
calls it after the nightly scrape loop (see pipeline.py._build_all_companies) so the
combined file reflects that run's freshest per-firm data, including firms the scraper
factory just generated tonight (written to local disk before their own deferred commit).

Run standalone (prints a summary instead of committing anything):
    python3 automation/master_builder.py [--data-dir PATH]
"""
from __future__ import annotations

import json
from pathlib import Path

import identity
import names

_HERE = Path(__file__).resolve().parent
_DEFAULT_DATA_DIR = _HERE.parent / "data"
_OUTPUT_FILENAME = "all_companies.json"


def _load_dataset(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:  # noqa: BLE001 — one bad file must not sink the whole build
        print(f"[master_builder] WARNING: could not read {path.name}, skipping")
        return []


def build(data_dir: Path | None = None) -> list[dict]:
    """Combine every real dataset in data_dir into one normalized list.

    Non-dataset files (gen_attempts.json, spend.json, discovered_candidates.json,
    reports, etc.) are excluded via identity.slug_from_file() — the same filter
    candidate_finder.py already uses to tell "is this a company dataset" from
    "is this pipeline memory", so this stays one fact, not two competing checks.

    _OUTPUT_FILENAME itself is also excluded: it ends in "_companies.json" like any
    real per-firm dataset, so identity.slug_from_file() happily assigns it a bogus
    slug ("all") and, left in, this function would re-ingest its own prior output as
    a fake firm on every run after the first — silently doubling the file.
    """
    data_dir = data_dir or _DEFAULT_DATA_DIR
    combined: list[dict] = []

    dataset_files = sorted(
        p for p in data_dir.glob("*.json")
        if p.name != _OUTPUT_FILENAME and identity.slug_from_file(p.name)
    )

    for path in dataset_files:
        slug = identity.slug_from_file(path.name)
        firm = names.display_name(path.name)
        records = _load_dataset(path)
        for r in records:
            name = identity.company_name(r)
            if not name:
                continue  # nothing to key this company on — skip rather than fabricate
            combined.append({
                "firm": firm,
                "firm_slug": slug,
                "name": name,
                "url": identity.company_url(r),
                "description": identity.company_desc(r),
                "everywhere_tags": r.get("everywhere_tags") or [],
                "exited": identity.is_exited(r),
            })

    return combined


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=str, default=None)
    args = ap.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else _DEFAULT_DATA_DIR
    rows = build(data_dir)
    firms = {r["firm_slug"] for r in rows}
    print(f"[master_builder] {len(rows)} companies across {len(firms)} firms")
    print(f"[master_builder] sample:")
    for r in rows[:3]:
        print(f"  {r['firm']:<20} {r['name']}")
