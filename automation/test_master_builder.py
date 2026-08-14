"""Offline tests for master_builder.py — no network, no cost.

What needs proving:
  1. every output record has a non-empty firm and name — nothing unattributed or
     unkeyable makes it into the combined file;
  2. field-alias normalization actually resolves values for real firms with
     different scraper schemas (identity.py's job, exercised here end to end);
  3. non-dataset files in data/ (gen_attempts.json, spend.json, reports, etc.) are
     excluded, not accidentally combined as if they were a firm's companies;
  4. a company with no description comes out null, not fabricated;
  5. build() never raises on a malformed dataset file — one bad file must not sink
     the whole nightly run.

Run:  python3 automation/test_master_builder.py     (exit 0 = all pass)
"""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import master_builder  # noqa: E402

_FAILS: list[str] = []


def check(label: str, got, want) -> None:
    ok = got == want
    if not ok:
        _FAILS.append(f"{label}: got {got!r}, want {want!r}")
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"   got={got!r} want={want!r}"))


def _write(dir_: pathlib.Path, name: str, content) -> None:
    (dir_ / name).write_text(json.dumps(content), encoding="utf-8")


def test_every_record_has_firm_and_name() -> None:
    print("\nevery output record has a non-empty firm and name")
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _write(d, "example_companies.json", [
            {"company_name": "Foo", "description": "desc"},
            {"name": "no idea, this scraper uses 'name'"},
        ])
        rows = master_builder.build(d)
        check("2 records in", len(rows), 2)
        for r in rows:
            check(f"{r['name']!r} has non-empty firm", bool(r["firm"]), True)
            check(f"{r['name']!r} has non-empty name", bool(r["name"]), True)


def test_field_alias_normalization() -> None:
    print("\nfield-alias normalization resolves across different scraper schemas")
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _write(d, "schema_a_companies.json", [
            {"company_name": "Stripe", "company_url": "https://stripe.com",
             "description": "Payments infra."},
        ])
        _write(d, "schema_b_companies.json", [
            {"name": "Ramp", "website": "https://ramp.com", "summary": "Corporate cards."},
        ])
        rows = master_builder.build(d)
        by_name = {r["name"]: r for r in rows}
        check("schema_a name resolved", by_name["Stripe"]["name"], "Stripe")
        check("schema_a url resolved", by_name["Stripe"]["url"], "https://stripe.com")
        check("schema_a desc resolved", by_name["Stripe"]["description"], "Payments infra.")
        check("schema_b name resolved (name key)", by_name["Ramp"]["name"], "Ramp")
        check("schema_b url resolved (website key)", by_name["Ramp"]["url"], "https://ramp.com")
        check("schema_b desc resolved (summary key)", by_name["Ramp"]["description"], "Corporate cards.")


def test_non_dataset_files_excluded() -> None:
    print("\nnon-dataset files in data/ are excluded")
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _write(d, "real_companies.json", [{"company_name": "OnlyRealOne"}])
        _write(d, "gen_attempts.json", [{"slug": "x", "attempts": 4}])
        _write(d, "spend.json", [{"month": "2026-08", "spent": 1.23}])
        _write(d, "discovered_candidates.json", [{"firm_name": "Something", "status": "queued"}])
        rows = master_builder.build(d)
        check("only the real dataset contributed", len(rows), 1)
        check("only company present", rows[0]["name"], "OnlyRealOne")


def test_missing_description_is_null_not_fabricated() -> None:
    print("\nmissing description stays null, never fabricated")
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _write(d, "nodesc_companies.json", [{"company_name": "NoDescCo"}])
        rows = master_builder.build(d)
        check("description is None", rows[0]["description"], None)


def test_malformed_file_does_not_crash_build() -> None:
    print("\na malformed dataset file is skipped, not a fatal error")
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        (d / "broken_companies.json").write_text("{not valid json", encoding="utf-8")
        _write(d, "fine_companies.json", [{"company_name": "StillWorks"}])
        rows = master_builder.build(d)
        check("the good file still produced its company", len(rows), 1)
        check("it's the good one", rows[0]["name"], "StillWorks")


def test_own_output_file_excluded_from_input() -> None:
    print("\nall_companies.json (own prior output) is never re-ingested as a firm")
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _write(d, "real_companies.json", [{"company_name": "RealCo"}])
        # simulate a prior run's committed output sitting in data/ on disk
        _write(d, "all_companies.json", [
            {"firm": "SomeFirm", "firm_slug": "somefirm", "name": "StaleCo",
             "url": None, "description": None, "everywhere_tags": [], "exited": False},
        ])
        rows = master_builder.build(d)
        check("only the real firm contributed", len(rows), 1)
        check("no bogus 'all' firm_slug", "all" in {r["firm_slug"] for r in rows}, False)
        check("stale re-ingested company absent", rows[0]["name"], "RealCo")


def test_exited_flag() -> None:
    print("\nexited status is detected from status-ish fields")
    with tempfile.TemporaryDirectory() as td:
        d = pathlib.Path(td)
        _write(d, "exit_companies.json", [
            {"company_name": "Acquired Co", "status": "acquired"},
            {"company_name": "Active Co", "status": "active"},
        ])
        rows = master_builder.build(d)
        by_name = {r["name"]: r for r in rows}
        check("acquired company flagged exited", by_name["Acquired Co"]["exited"], True)
        check("active company not flagged exited", by_name["Active Co"]["exited"], False)


if __name__ == "__main__":
    test_every_record_has_firm_and_name()
    test_field_alias_normalization()
    test_non_dataset_files_excluded()
    test_missing_description_is_null_not_fabricated()
    test_malformed_file_does_not_crash_build()
    test_own_output_file_excluded_from_input()
    test_exited_flag()
    print()
    if _FAILS:
        print(f"{len(_FAILS)} FAILURE(S)")
        for f in _FAILS:
            print(" -", f)
        sys.exit(1)
    print("all tests passed")
