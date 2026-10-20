"""Builds data/all_companies.json (+ all_companies_2.json, _3 … overflow parts) —
every firm's dataset combined, split across part files of at most ~40 MB each,
each record tagged with which firm it came from and normalized through identity.py's
field-alias rules (site-tailored schemas mean "company name" comes in under a dozen
different keys across the 61+ bespoke scrapers; identity.py already solves this, this
module just applies it once across every dataset instead of once per firm).

Pure/offline: build() only reads local files, no network or GitHub calls. The pipeline
calls it after the nightly scrape loop (see pipeline.py._build_all_companies) so the
combined file reflects that run's freshest per-firm data, including firms the scraper
factory just generated tonight (written to local disk before their own deferred commit).

Split into parts (2026-10-18): GitHub/raw consumers choke on one 50+ MB file, so the
combined list is written in order across part files, splitting only on whole-firm
boundaries: all_companies.json is filled up to PART_LIMIT_BYTES (~40 MB), then the
overflow spills into all_companies_2.json, all_companies_3.json, … Every part keeps
the same structure (a JSON list of company rows). data/all_companies_index.json lists
the parts with firm/company counts. Readers should use load_all() (or read the index
and concatenate every part) — never assume all_companies.json alone is the full set.

Run standalone (writes the part files + index locally; commits nothing):
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
_OUTPUT_FILENAME = "all_companies.json"          # part 1 (kept for compatibility)
INDEX_FILENAME = "all_companies_index.json"
PART_LIMIT_BYTES = 40_000_000                    # ~40 MB per part file
_PART_RE = __import__("re").compile(r"^all_companies(?:_(\d+))?\.json$")


def part_filename(i: int) -> str:
    """0-based part index -> file name: all_companies.json, all_companies_2.json, …"""
    return _OUTPUT_FILENAME if i == 0 else f"all_companies_{i + 1}.json"


def is_master_file(name: str) -> bool:
    """True for any combined-output part file or the index (never a firm dataset)."""
    return bool(_PART_RE.match(name)) or name == INDEX_FILENAME


def _dumps(rows) -> str:
    return json.dumps(rows, indent=2, ensure_ascii=False) + "\n"

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
        if not is_master_file(p.name) and identity.slug_from_file(p.name)
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
            # Never-remove rule (2026-10-20): carry listing dates when the dataset has them.
            for k in ("listed_on_site", "first_seen", "last_seen", "delisted_date"):
                if k in r:
                    row[k] = r[k]
            combined.append(row)

    return combined


def split_parts(rows: list[dict], limit: int = PART_LIMIT_BYTES) -> list[list[dict]]:
    """Split rows (in order) into parts on whole-firm boundaries, filling each part
    up to `limit` bytes of serialized JSON before spilling into the next. A single
    firm larger than `limit` gets a part of its own (never split across files)."""
    # contiguous firm blocks in existing order
    blocks: list[list[dict]] = []
    for r in rows:
        if blocks and blocks[-1][0]["firm_slug"] == r["firm_slug"]:
            blocks[-1].append(r)
        else:
            blocks.append([r])

    def row_bytes(r: dict) -> int:
        # size of one element inside the indent=2 list: every line gains 2 spaces,
        # plus ",\n" separator
        txt = json.dumps(r, indent=2, ensure_ascii=False)
        return len(txt.encode("utf-8")) + 2 * (txt.count("\n") + 1) + 2

    parts: list[list[dict]] = []
    cur: list[dict] = []
    cur_bytes = 4  # "[\n" + "]\n"
    for b in blocks:
        bb = sum(row_bytes(r) for r in b)
        if cur and cur_bytes + bb > limit:
            parts.append(cur)
            cur, cur_bytes = [], 4
        cur.extend(b)
        cur_bytes += bb
    if cur or not parts:
        parts.append(cur)
    return parts


def build_index(parts: list[list[dict]]) -> dict:
    entries = []
    for i, p in enumerate(parts):
        firms = []
        for r in p:
            if not firms or firms[-1] != r["firm_slug"]:
                firms.append(r["firm_slug"])
        entries.append({
            "file": part_filename(i),
            "firms": len(set(firms)),
            "companies": len(p),
            "bytes": len(_dumps(p).encode("utf-8")),
            "first_firm": p[0]["firm"] if p else None,
            "last_firm": p[-1]["firm"] if p else None,
        })
    return {
        "_comment": "Combined company master, split on whole-firm boundaries into "
                    "parts of <= ~40 MB. Concatenate every part (in this order) for "
                    "the full list. Built by automation/master_builder.py.",
        "part_limit_bytes": PART_LIMIT_BYTES,
        "total_firms": len({r["firm_slug"] for p in parts for r in p}),
        "total_companies": sum(len(p) for p in parts),
        "parts": entries,
    }


def write_parts(rows: list[dict], data_dir: Path | None = None,
                limit: int = PART_LIMIT_BYTES) -> dict:
    """Write all part files + index to data_dir; remove stale higher-numbered parts.
    Returns the index dict."""
    data_dir = data_dir or _DEFAULT_DATA_DIR
    parts = split_parts(rows, limit)
    for i, p in enumerate(parts):
        (data_dir / part_filename(i)).write_text(_dumps(p), encoding="utf-8")
    keep = {part_filename(i) for i in range(len(parts))}
    for f in data_dir.glob("all_companies*.json"):
        if _PART_RE.match(f.name) and f.name not in keep:
            f.unlink()
    idx = build_index(parts)
    (data_dir / INDEX_FILENAME).write_text(
        json.dumps(idx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return idx


def part_files(data_dir: Path | None = None) -> list[Path]:
    """Existing part files in order (from the index when present)."""
    data_dir = data_dir or _DEFAULT_DATA_DIR
    idx_path = data_dir / INDEX_FILENAME
    if idx_path.exists():
        try:
            idx = json.loads(idx_path.read_text(encoding="utf-8"))
            return [data_dir / e["file"] for e in idx.get("parts", [])]
        except Exception:  # noqa: BLE001 — fall back to globbing
            pass
    found = []
    for f in data_dir.glob("all_companies*.json"):
        m = _PART_RE.match(f.name)
        if m:
            found.append((int(m.group(1) or 1), f))
    return [f for _, f in sorted(found)]


def load_all(data_dir: Path | None = None) -> list[dict]:
    """Read every part and return the full combined company list (in order)."""
    rows: list[dict] = []
    for f in part_files(data_dir):
        data = json.loads(f.read_text(encoding="utf-8"))
        rows.extend(data if isinstance(data, list) else [])
    return rows


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=str, default=None)
    args = ap.parse_args()

    data_dir = Path(args.data_dir) if args.data_dir else _DEFAULT_DATA_DIR
    rows = build(data_dir)
    idx = write_parts(rows, data_dir)
    firms = {r["firm_slug"] for r in rows}
    for e in idx["parts"]:
        print(f"[master_builder] wrote {data_dir / e['file']} — {e['companies']} companies, "
              f"{e['firms']} firms, {e['bytes']:,} bytes")
    print(f"[master_builder] total {len(rows)} companies across {len(firms)} firms "
          f"in {len(idx['parts'])} part(s); index {data_dir / INDEX_FILENAME}")
    print(f"[master_builder] sample:")
    for r in rows[:3]:
        print(f"  {r['firm']:<20} {r['name']}")
