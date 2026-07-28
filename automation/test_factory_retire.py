"""Offline tests for terminal factory retirement — no network, no key, no cost.

The rule under test (user decision 2026-07-27): if no portfolio page resolves
in the factory's step 1, the firm is retired the SAME night. Before this, a
no-url firm burned its whole 4-attempt budget one counted no-op per night
(~2 weeks of "needs-scraper" in Airtable) because the failure shared a counter
designed for generation failures, where retries-with-feedback actually help.

What needs proving, last one most:

  1. attempt() marks a no-url result terminal without touching the network;
  2. one terminal failure retires the firm at once — honestly (attempts stays
     1, "retired": true; NOT attempts jammed to the max);
  3. a transport fluke can never retire a firm, terminal or not;
  4. a firm retiring with NO dataset vanishes from Airtable (in-run row
     dropped, old row queued for deletion), while a firm WITH a dataset keeps
     its row — Airtable is "firms with data", not a graveyard of attempts;
  5. it actually stops the nightly burn: 30 simulated nights must record
     exactly ONE attempt. A flag that looked right but left the firm in
     targets() would pass every unit test above and fix nothing.

Run:  python3 automation/test_factory_retire.py     (exit 0 = all pass)
"""
from __future__ import annotations

import pathlib
import sys
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import airtable_writer  # noqa: E402
import gen_state  # noqa: E402
import scraper_factory  # noqa: E402

_FAILS: list[str] = []


def check(label: str, got, want) -> None:
    ok = got == want
    if not ok:
        _FAILS.append(f"{label}: got {got!r}, want {want!r}")
    print(f"  {'ok  ' if ok else 'FAIL'} {label}"
          + ("" if ok else f"   got={got!r} want={want!r}"))


def _firm(slug: str = "nourlfirm") -> SimpleNamespace:
    # homepage=None means attempt() cannot even try to resolve — it must
    # return terminal before any network or API call.
    return SimpleNamespace(slug=slug, data_file=f"{slug}_companies.json",
                           firm_name="No URL Firm", kind="generic",
                           homepage=None, portfolio_url=None)


def test_attempt_is_terminal_offline() -> None:
    print("\nattempt(): no portfolio url is terminal, decided offline")
    r = scraper_factory.attempt(_firm(), None, tries=4)
    check("reason", r["reason"], "no portfolio url")
    check("terminal flag", r["terminal"], True)
    check("exactly one failure (burst never started)", len(r["failures"]), 1)
    check("no success", r["ok"], False)


def test_terminal_retires_at_once_and_honestly() -> None:
    print("\ngen_state: one terminal failure = retired, with honest bookkeeping")
    st: dict = {}
    gen_state.record_failure(st, "nourlfirm", "no portfolio url", terminal=True)
    ok, why = gen_state.eligible(st, "nourlfirm")
    check("ineligible immediately", ok, False)
    check("reason names the cause", "no portfolio url" in why, True)
    check("attempts stays 1, not jammed to max", st["nourlfirm"]["attempts"], 1)
    check("retired flag set", st["nourlfirm"].get("retired"), True)
    # escape hatch unchanged: clearing the entry re-arms the firm
    gen_state.clear(st, "nourlfirm")
    check("clearing the entry re-arms", gen_state.eligible(st, "nourlfirm")[0],
          True)


def test_transport_fluke_never_retires() -> None:
    print("\ngen_state: transport errors stay uncounted and cannot retire")
    st: dict = {}
    gen_state.record_failure(st, "flaky", "generation error: timeout",
                             terminal=True)   # belt-and-braces: even if flagged
    check("uncounted", st["flaky"]["attempts"], 0)
    check("not retired", st["flaky"].get("retired", False), False)
    check("still eligible", gen_state.eligible(st, "flaky")[0], True)


def test_no_dataset_retiree_vanishes_from_airtable() -> None:
    print("\npipeline: a no-data retiree is deleted, a with-data one is kept")
    import pipeline

    # no dataset on disk -> row dropped from the upsert, delete queued
    firm = _firm()
    registry = [{"data_file": firm.data_file, "status": "needs-scraper"},
                {"data_file": "other_companies.json", "status": "active"}]
    at_deletes: list = []
    registry = pipeline._retire_from_airtable(firm, registry, at_deletes)
    check("its in-run row is dropped",
          [h["data_file"] for h in registry], ["other_companies.json"])
    check("its old row is queued for deletion", at_deletes,
          [firm.data_file])

    # a real dataset on disk (thin is still real) -> row untouched
    wing = _firm("wingvc")            # data/wingvc_companies.json exists
    registry = [{"data_file": wing.data_file, "status": "needs-scraper"}]
    at_deletes = []
    registry = pipeline._retire_from_airtable(wing, registry, at_deletes)
    check("a with-data firm keeps its row",
          [h["data_file"] for h in registry], [wing.data_file])
    check("and is never deleted", at_deletes, [])

    # the writer's guards: nothing to delete costs nothing, dry-run is inert
    check("empty delete list is a no-op", airtable_writer.delete_firms([]), 0)
    check("dry-run deletes nothing",
          airtable_writer.delete_firms(["x_companies.json"], dry_run=True), 0)

    # the reconcile pass refuses a broken keep-set: a glob bug upstream must
    # never be amplified into emptying the whole table
    check("empty keep-set refuses to mass-delete",
          airtable_writer.delete_strays(set()), 0)
    check("tiny keep-set refuses too",
          airtable_writer.delete_strays({"a_companies.json"}), 0)
    big_keep = {f"firm{i}_companies.json" for i in range(52)}
    check("sane keep-set proceeds (dry-run)",
          airtable_writer.delete_strays(big_keep, dry_run=True), 0)


def test_thirty_nights_record_one_attempt() -> None:
    print("\nsimulation: 30 nights, exactly one attempt ever recorded")
    st: dict = {}
    firm = _firm()
    recorded = 0
    for _night in range(30):
        targets = scraper_factory.targets([firm], st)
        if firm.slug not in {f.slug for f in targets}:
            continue                       # skipped before any work — the point
        r = scraper_factory.attempt(firm, None, tries=4)
        for fail in r["failures"]:
            gen_state.record_failure(st, firm.slug, fail,
                                     terminal=r.get("terminal", False))
            recorded += 1
    check("attempts recorded across 30 nights", recorded, 1)
    check("state agrees", st[firm.slug]["attempts"], 1)
    check("retired", st[firm.slug].get("retired"), True)


if __name__ == "__main__":
    test_attempt_is_terminal_offline()
    test_terminal_retires_at_once_and_honestly()
    test_transport_fluke_never_retires()
    test_no_dataset_retiree_vanishes_from_airtable()
    test_thirty_nights_record_one_attempt()
    print()
    if _FAILS:
        print(f"{len(_FAILS)} FAILURE(S)")
        for f in _FAILS:
            print(" -", f)
        sys.exit(1)
    print("all tests passed")
