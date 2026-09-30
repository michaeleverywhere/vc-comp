#!/usr/bin/env python3
"""Normalize stage / first-invested-related fields to funding-round labels.

Only maps values that already encode a round on firm-site data
(pre-seed, seed, Series A/B/C/…, and similar firm-site labels).
Non-round values (Early, Growth, Venture, partner names, Private, years,
exit labels, etc.) become empty — never invent rounds from other sources.

Does not overwrite a good round label with a worse one when consolidating.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# Fields that should hold a funding-round label (or be empty).
STAGE_FIELDS = (
    "stage",
    "current_stage",
    "initial_investment_stage",
    "investment_stage",
    "first_partnered_stage",
    "first_invested_stage",
    "investment_stages",
    "type",
    "initial_investment_type",
)

# first_invested is often a year/date — only rewrite when the value itself encodes a round.
FIRST_INVESTED_FIELD = "first_invested"

# Canonical round labels (display form) → quality score (higher = better / more specific).
# Multi-round firm-site labels score below a single specific series letter.
_SERIES_RE = re.compile(
    r"\bseries[\s\-]*([a-z])\b",
    re.I,
)
_SERIES_PLUS_RE = re.compile(
    r"\bseries[\s\-]*([a-z])\s*\+|series\s*([a-z])\s*or\s*later\b",
    re.I,
)
_PRE_SEED_RE = re.compile(r"\bpre[\s\-]*seed\b", re.I)
_SEED_RE = re.compile(r"\bseed\b", re.I)
_ANGEL_RE = re.compile(r"\bangel\b", re.I)
_PRE_SERIES_A_RE = re.compile(r"\bpre[\s\-]*series[\s\-]*a\b", re.I)

# Values / tokens that are explicitly NOT funding rounds (clear these).
_NON_ROUND_EXACT = {
    "early", "early stage", "growth", "growth stage", "late stage", "later-stage",
    "later stage", "venture", "venture capital", "private", "private equity",
    "acquired", "exited", "exit", "completed", "ipo", "public", "spac", "dpo",
    "m&a", "buyout", "public/pipes", "common stock", "common", "token",
    "current", "past", "co-invest", "studio", "anchor", "digital asset",
    "special opportunities - brazil",
}

# Year-only / date-like — leave first_invested alone; clear if in a stage field.
_YEAR_RE = re.compile(r"^\d{4}$")
_DATE_RE = re.compile(
    r"^(\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2}|[A-Za-z]+\s+\d{4})$"
)


def _quality(label: str) -> int:
    """Higher = more specific round. Used to avoid overwriting good with worse."""
    if not label:
        return 0
    low = label.lower().strip()
    # Single Series letter (Series A) — best
    m = re.fullmatch(r"series\s+([a-z])", low)
    if m:
        return 100 + (ord(m.group(1)) - ord("a"))  # A=100 … slight tie-break
    if low in ("pre-seed", "preseed"):
        return 90
    if low == "seed":
        return 88
    if low == "angel":
        return 85
    if low == "pre-series a":
        return 87
    # Series C+ / Series C or Later
    if re.fullmatch(r"series\s+[a-z]\+|series\s+[a-z]\s+or\s+later", low):
        return 70
    # Multi-round firm-site labels e.g. "Pre-Seed / Seed", "Seed / Series A"
    if "/" in label or " + " in low or " and " in low:
        return 50
    return 40


def _canon_series(letter: str, plus: bool = False) -> str:
    letter = letter.upper()
    return f"Series {letter}+" if plus else f"Series {letter}"


def extract_rounds(raw) -> list[str]:
    """Extract ordered unique canonical round labels from a raw field value."""
    if raw is None:
        return []
    if isinstance(raw, (int, float)):
        return []  # years etc.
    if isinstance(raw, list):
        parts = []
        for x in raw:
            parts.extend(extract_rounds(x))
        return _dedupe(parts)
    if not isinstance(raw, str):
        raw = str(raw)
    s = raw.strip()
    if not s:
        return []

    # Split common multi-value separators but keep "Pre-Seed / Seed" style for later.
    # First try the whole string; also scan segments.
    segments = re.split(r"[|,;]+", s)
    found: list[str] = []
    for seg in segments:
        found.extend(_extract_from_segment(seg.strip()))
    return _dedupe(found)


def _extract_from_segment(seg: str) -> list[str]:
    if not seg:
        return []
    low = seg.lower().strip()

    # Exact non-rounds
    if low in _NON_ROUND_EXACT:
        return []
    if _YEAR_RE.match(seg) or _DATE_RE.match(seg):
        return []
    # Partner-name junk / fund labels / "StageSeries A" handled via regex below
    if low.startswith("fund ") or re.fullmatch(r"fund\s+[ivxlcdm]+", low):
        return []
    if low.startswith("acquired") or "acquired by" in low:
        # May still embed a round earlier: "Series A in 2018 Acquired by …"
        pass
    if low.startswith("initial investment") or low.startswith("investment in"):
        return []

    # Strip leading "Stage" glue from bad scrapes: StageSeries A, StageSeed
    seg2 = re.sub(r"^stage\s*", "", seg, flags=re.I).strip()
    low2 = seg2.lower()

    rounds: list[str] = []

    # Pre-Series A
    if _PRE_SERIES_A_RE.search(seg2):
        rounds.append("Pre-Series A")

    # Series X+ / Series X or Later
    for m in re.finditer(
        r"series[\s\-]*([a-z])\s*\+|series[\s\-]*([a-z])\s+or\s+later",
        seg2,
        re.I,
    ):
        letter = (m.group(1) or m.group(2)).upper()
        rounds.append(f"Series {letter}+")

    # Series X (plain) — also from "series-a", "Led Series A", "Series A in 2018"
    for m in re.finditer(r"(?:led\s+|co-led\s+)?series[\s\-]*([a-z])\b", seg2, re.I):
        letter = m.group(1).upper()
        # Avoid double-counting if we already got Series X+ for same letter from plus form
        label = f"Series {letter}"
        plus = f"Series {letter}+"
        if plus not in rounds:
            rounds.append(label)

    # Pre-Seed
    if _PRE_SEED_RE.search(seg2):
        rounds.append("Pre-Seed")

    # Seed (but not if only matched inside pre-seed — pre-seed already added)
    # Match seed with optional Led/Co-led
    if re.search(r"(?:led\s+|co-led\s+)?\bseed\b", seg2, re.I):
        # If the only seed hit is inside "pre-seed", don't also add Seed unless
        # there's a separate seed mention.
        # Simple approach: if "pre-seed" present and no other seed context like
        # "Pre-Seed / Seed" or "Seed +", check carefully.
        if re.search(
            r"(?:^|[\s/,;|+]|led\s+|co-led\s+)seed(?:\b|[\s/,;|+])",
            re.sub(r"pre[\s\-]*seed", "«PRE»", seg2, flags=re.I),
            re.I,
        ) or re.search(r"\bseed\b", re.sub(r"pre[\s\-]*seed", "«PRE»", seg2, flags=re.I), re.I):
            # After masking pre-seed, is there still a seed?
            masked = _PRE_SEED_RE.sub("«PRE»", seg2)
            if _SEED_RE.search(masked):
                rounds.append("Seed")
        elif "pre-seed" not in low2 and "preseed" not in low2.replace("-", ""):
            rounds.append("Seed")

    # Angel
    if _ANGEL_RE.search(seg2) and "angel-seed" not in low2:
        rounds.append("Angel")
    if "angel-seed" in low2 or re.search(r"angel[\s\-/]+seed", low2):
        for x in ("Angel", "Seed"):
            if x not in rounds:
                rounds.append(x)

    # Secondary — firm-site label; keep as Secondary when clearly that round type
    if re.search(r"\bsecondary\b", seg2, re.I):
        rounds.append("Secondary")

    return rounds


def _dedupe(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    # If we have both Series A and Series A+, keep the plus only? Prefer plus as stated.
    # If both Series C and Series C+, drop plain Series C.
    for letter in "ABCDEFGH":
        plain, plus = f"Series {letter}", f"Series {letter}+"
        if plain in seen and plus in seen:
            out = [x for x in out if x != plain]
    return out


_ROUND_ORDER = {
    "Pre-Seed": 0,
    "Angel": 1,
    "Seed": 2,
    "Pre-Series A": 3,
    "Secondary": 50,
}
for _i, _letter in enumerate("ABCDEFGH"):
    _ROUND_ORDER[f"Series {_letter}"] = 10 + _i
    _ROUND_ORDER[f"Series {_letter}+"] = 10 + _i + 0.5


def _round_sort_key(label: str):
    return (_ROUND_ORDER.get(label, 40), label)


def format_rounds(rounds: list[str]) -> str | None:
    if not rounds:
        return None
    rounds = sorted(rounds, key=_round_sort_key)
    if len(rounds) == 1:
        return rounds[0]
    # Preserve a readable firm-site multi-label, earliest-first
    return " / ".join(rounds)


def normalize_round_value(raw) -> tuple[object | None, bool]:
    """Normalize a stage-like value to a clear round string/list, or empty.

    Returns (new_value, did_change).
    """
    if raw is None:
        return None, False
    if isinstance(raw, str) and not raw.strip():
        return (None, True) if raw != "" else (None, False)

    was_list = isinstance(raw, list)
    rounds = extract_rounds(raw)

    if was_list:
        old_items = [str(x).strip() for x in raw if x not in (None, "")]
        if rounds == old_items:
            return rounds, False
        # If every old item already canonical-equal ignoring case
        if [r.lower() for r in rounds] == [o.lower() for o in old_items] and len(rounds) == len(old_items):
            # rewrite casing only
            return rounds, rounds != old_items
        return rounds, True

    new = format_rounds(rounds)
    if isinstance(raw, (int, float)):
        return None, True
    old_s = str(raw).strip()
    if new is None:
        return None, bool(old_s)
    return new, new != old_s


# Prefer first-invested / initial keys over current_stage so a later "current"
# label cannot overwrite a good first-check round (and vice versa for junk).
_BEST_ROUND_KEY_PRIORITY = (
    "first_invested_stage",
    "first_partnered_stage",
    "initial_investment_type",
    "initial_investment_stage",
    "investment_stage",
    "investment_stages",
    "stage",
    "type",
    "current_stage",
    FIRST_INVESTED_FIELD,
)


def best_round_from_record(record: dict) -> str | None:
    """Pick a clear funding-round label from the record (no inventing).

    Walks first-invested-related keys before current_stage. Among values that
    already encode a round, prefers higher-quality labels so Early/Growth never
    displace Series A / Seed.
    """
    best_label = None
    best_q = -1
    for k in _BEST_ROUND_KEY_PRIORITY:
        if k not in record:
            continue
        rounds = extract_rounds(record.get(k))
        label = format_rounds(rounds)
        if not label:
            continue
        # Quality of the earliest/primary token in a multi-label
        primary = label.split(" / ")[0]
        q = _quality(primary)
        if q > best_q:
            best_q = q
            best_label = label
            # First priority key with a strong round wins outright
            if q >= 85:
                return best_label
    return best_label


def _looks_like_year_or_date(raw) -> bool:
    if isinstance(raw, (int, float)):
        return True
    if not isinstance(raw, str):
        return False
    s = raw.strip()
    return bool(_YEAR_RE.match(s) or _DATE_RE.match(s) or re.match(r"^\d{4}-\d{2}", s))


def normalize_record(record: dict) -> dict:
    """Mutate record in place; return stats dict."""
    stats = Counter()
    for k in STAGE_FIELDS:
        if k not in record:
            continue
        old = record.get(k)
        if old in (None, "", [], {}):
            continue
        new, changed = normalize_round_value(old)
        if not changed and new == old:
            if new not in (None, "", []):
                stats["already_good"] += 1
            continue
        if new in (None, "", []):
            # Clear non-round
            if isinstance(old, list):
                record[k] = []
            else:
                record[k] = None
            stats["cleared_non_round"] += 1
            stats[f"cleared:{old if not isinstance(old, list) else '|'.join(map(str, old))}"] += 1
        else:
            record[k] = new
            stats["rewritten"] += 1
            stats[f"rewrite:{old!s}->{new!s}"] += 1

    # first_invested: only touch when value encodes a round (not year/date)
    if FIRST_INVESTED_FIELD in record:
        old = record.get(FIRST_INVESTED_FIELD)
        if old not in (None, "", [], {}) and not _looks_like_year_or_date(old):
            rounds = extract_rounds(old)
            if rounds:
                new = format_rounds(rounds)
                if new and new != old:
                    record[FIRST_INVESTED_FIELD] = new
                    stats["rewritten"] += 1
            # If it doesn't encode a round and isn't a date, leave as-is
            # (don't clear unknown first_invested strings that might be dates we didn't parse)

    return stats


def iter_dataset_files(data_dir: Path):
    for path in sorted(data_dir.glob("*.json")):
        # per-firm datasets only
        name = path.name
        if name == "all_companies.json":
            continue
        if name.endswith("_companies.json") or name == "companies.json":
            yield path


def main() -> int:
    dry = "--dry-run" in sys.argv
    total_records = 0
    files_touched = 0
    aggregate = Counter()
    rewrite_examples = Counter()
    clear_examples = Counter()

    for path in iter_dataset_files(DATA):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"SKIP {path.name}: {e}")
            continue
        if not isinstance(data, list):
            continue
        file_changed = False
        for rec in data:
            if not isinstance(rec, dict):
                continue
            total_records += 1
            before = json.dumps(rec, sort_keys=True, default=str)
            stats = normalize_record(rec)
            after = json.dumps(rec, sort_keys=True, default=str)
            if before != after:
                file_changed = True
            for k, v in stats.items():
                if k.startswith("rewrite:"):
                    rewrite_examples[k[len("rewrite:"):]] += v
                elif k.startswith("cleared:"):
                    clear_examples[str(k[len("cleared:"):])[:80]] += v
                else:
                    aggregate[k] += v
        if file_changed:
            files_touched += 1
            if not dry:
                path.write_text(
                    json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )

    report = {
        "dry_run": dry,
        "records_scanned": total_records,
        "files_touched": files_touched,
        "rewritten": aggregate.get("rewritten", 0),
        "cleared_non_round": aggregate.get("cleared_non_round", 0),
        "already_good": aggregate.get("already_good", 0),
        "top_rewrites": rewrite_examples.most_common(40),
        "top_clears": clear_examples.most_common(40),
    }
    out = ROOT / "artifacts" / "stage_norm_report.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in report if k not in ("top_rewrites", "top_clears")}, indent=2))
    print("top rewrites:")
    for a, c in report["top_rewrites"][:25]:
        print(f"  {c:5d} | {a}")
    print("top clears:")
    for a, c in report["top_clears"][:25]:
        print(f"  {c:5d} | {a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
