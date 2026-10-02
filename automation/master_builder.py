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
import sys
from pathlib import Path

import identity
import names

# Round normalizer lives in scripts/ — reuse so export matches per-firm files.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
try:
    from normalize_stages import best_round_from_record, extract_rounds, format_rounds
except ImportError:  # pragma: no cover
    best_round_from_record = None  # type: ignore
    extract_rounds = None  # type: ignore
    format_rounds = None  # type: ignore

_HERE = Path(__file__).resolve().parent
_DEFAULT_DATA_DIR = _HERE.parent / "data"
_OUTPUT_FILENAME = "all_companies.json"

_LOC_KEYS = ("location", "headquarters", "hq", "hq_location")
_STAGE_KEYS = (
    "stage", "current_stage", "initial_investment_stage", "investment_stage",
    "first_partnered_stage", "first_invested_stage", "investment_stages",
    "initial_investment_type",  # accel/menlo/usv: series-a / seed / …
)
_FIRST_KEYS = (
    "first_invested", "first_invested_year", "first_invest_year",
    "first_investment_year", "first_investment_date", "first_partnered_year",
    "year_partnered", "bvp_partnered_year", "gc_backed_since_year",
    "invested_year", "initial_investment_date", "gc_backed_since", "first_partnered_date",
)


def _nonempty(v) -> bool:
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


def _first_present(record: dict, keys: tuple):
    for k in keys:
        if k in record and _nonempty(record.get(k)):
            v = record[k]
            if isinstance(v, list):
                # investment_stages etc. — join for the flat export
                return ", ".join(str(x) for x in v if x not in (None, ""))
            return v
    return None


def _status_of(record: dict):
    """Prefer explicit status; else map clear exit/active flags to active|acquired."""
    s = record.get("status")
    if isinstance(s, str) and s.strip():
        return s.strip()
    if record.get("is_acquired") is True:
        return "acquired"
    if record.get("acquirer"):
        return "acquired"
    if identity.is_exited(record):
        return "acquired"
    if record.get("is_current_investment") is True or record.get("is_active") is True:
        return "active"
    return None



def _stage_of(record: dict):
    """Funding-round label only. Prefer the best clear round across stage-like
    keys; leave null when firm-site data has no round (never invent)."""
    if best_round_from_record is not None:
        # Restrict to keys that exist on the record so we don't invent.
        return best_round_from_record(record)
    # Fallback without normalizer: first present value that extractably looks
    # like a round is unavailable — return raw first present.
    return _first_present(record, _STAGE_KEYS)


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
            row = {
                "firm": firm,
                "firm_slug": slug,
                "name": name,
                "url": identity.company_url(r),
                "description": identity.company_desc(r),
                "everywhere_tags": r.get("everywhere_tags") or [],
                "exited": identity.is_exited(r),
                # Conceptual Private Comps columns (null when source schema lacks them)
                "primary_investor": firm,
                "location": _first_present(r, _LOC_KEYS),
                "stage": _stage_of(r),
                "first_invested": _first_present(r, _FIRST_KEYS),
                "status": _status_of(r),
            }
            combined.append(row)

    return combined


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=str, default=None)
    args = ap.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else _DEFAULT_DATA_DIR
    rows = build(data_dir)
    out = data_dir / _OUTPUT_FILENAME
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    firms = {r["firm_slug"] for r in rows}
    print(f"[master_builder] wrote {out} — {len(rows)} companies across {len(firms)} firms")
    print(f"[master_builder] sample:")
    for r in rows[:3]:
        print(f"  {r['firm']:<20} {r['name']}")
