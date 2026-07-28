"""One-off LLM tag backfill for companies with NO text signal.

Context (2026-07-27, user decision): the tags are the product — the dashboard
agent builds comps from everywhere_tags — and after the shared keyword tagger
ran over every dataset, ~1,900 companies remained untaggable because their
records carry no description or sectors (coatue, generalcatalyst, ribbit,
wingvc, signalfire, homebrew…). The keyword approach is out of signal, so this
script asks Claude (Haiku by default) to classify each remaining company by
name + domain + firm context into the 17-tag taxonomy.

This deliberately breaks the "tagging is keyword-based, no LLM" convention,
ONCE, by explicit user decision. The recurring mechanisms stay keyword-based;
what this script writes survives weekly refreshes via tags.carry_forward.

Honesty rules:
  * the model is told to return [] for companies it does not confidently
    recognize — an empty tag is acceptable, a guessed one is not;
  * every returned tag is validated against the taxonomy (verbatim, cap 4);
    anything else is dropped;
  * fills ONLY records whose everywhere_tags is empty at write time;
  * every fill is logged to data/llm_tag_report.json (model, date, per-company
    tags) — same provenance idea as enrichment_report.json;
  * spend is booked to the ledger (data/spend.json, source "tag-backfill"),
    so the monthly budget stays truthful.

Run from the repo root ON A MACHINE WITH NETWORK ACCESS (the Cowork sandbox
cannot reach api.anthropic.com):

    python3 automation/llm_tag_backfill.py --limit 40   # smoke test, ~1 call
    python3 automation/llm_tag_backfill.py              # full pass (~$0.2)

Reads ANTHROPIC_API_KEY from the environment or automation/.env.
Idempotent: a second run only touches companies still untagged.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import budget  # noqa: E402
import tags  # noqa: E402

_DATA = Path(__file__).resolve().parent.parent / "data"
_REPORT = _DATA / "llm_tag_report.json"
_BATCH = 40
_MODEL_DEFAULT = os.environ.get("LLM_TAG_MODEL", "claude-haiku-4-5")

_PROMPT = """You classify venture-backed companies into a fixed tag taxonomy.

The ONLY allowed tags (verbatim):
{taxonomy}

Rules:
- 0 to 4 tags per company, most relevant first; most companies need 1-2.
- AI is not a category: classify an AI company by the market it serves.
- Use the investing firm named in parentheses only as weak context.
- If you do not confidently recognize the company, return [] for it. An empty
  answer is correct and welcome; a guessed tag is an error.

Companies:
{companies}

Reply with ONLY a JSON object mapping each number to its tag list, e.g.
{{"1": ["FinTech / Insurance"], "2": []}}"""


def _load_env() -> None:
    p = Path(__file__).resolve().parent / ".env"
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _domain(rec: dict) -> str:
    url = (rec.get("company_url") or rec.get("url") or "").lower()
    url = url.split("//")[-1].split("/")[0]
    return url[4:] if url.startswith("www.") else url


def collect() -> list[tuple[Path, int, dict]]:
    """(file, record-index, record) for every untagged company, stable order."""
    out = []
    for p in sorted(_DATA.glob("*_companies.json")):
        recs = json.loads(p.read_text())
        for i, r in enumerate(recs):
            if not r.get("everywhere_tags") and (
                    r.get("company_name") or r.get("name")):
                out.append((p, i, r))
    return out


def parse_reply(text: str, n: int) -> dict[int, list[str]]:
    """Strict-ish parse: first JSON object in the reply; every tag must be
    verbatim taxonomy or it is dropped; cap 4; unknown keys ignored."""
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {}
    try:
        raw = json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}
    tagset = set(tags.TAGS)
    out: dict[int, list[str]] = {}
    for k, v in (raw.items() if isinstance(raw, dict) else []):
        try:
            i = int(k)
        except (TypeError, ValueError):
            continue
        if 1 <= i <= n and isinstance(v, list):
            clean = [t for t in v if t in tagset]
            out[i] = list(dict.fromkeys(clean))[:4]
    return out


def _call(model: str, prompt: str) -> tuple[str, dict]:
    import requests
    r = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        json={"model": model, "max_tokens": 1500, "temperature": 0,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=120)
    r.raise_for_status()
    d = r.json()
    text = "".join(b.get("text", "") for b in d.get("content", []))
    return text, d.get("usage", {})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0,
                    help="max companies this run (0 = all)")
    ap.add_argument("--model", default=_MODEL_DEFAULT)
    ap.add_argument("--dry-run", action="store_true",
                    help="collect and print counts; no API calls, no writes")
    args = ap.parse_args()

    _load_env()
    todo = collect()
    if args.limit:
        todo = todo[: args.limit]
    per_file: dict[Path, int] = {}
    for p, _, _ in todo:
        per_file[p] = per_file.get(p, 0) + 1
    print(f"[tag-backfill] {len(todo)} untagged companies across "
          f"{len(per_file)} files")
    if args.dry_run or not todo:
        for p, n in sorted(per_file.items(), key=lambda x: -x[1])[:10]:
            print(f"    {p.name:40s} {n}")
        return 0
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[tag-backfill] no ANTHROPIC_API_KEY in env or automation/.env")
        return 1

    bstate = budget.load()
    budget.activate(bstate)
    ok_budget, why = budget.can_find(bstate)   # cheapest gate: is there money?
    if not ok_budget:
        print(f"[tag-backfill] refusing: {why}")
        return 1

    taxonomy = "\n".join(f"- {t}" for t in tags.TAGS)
    report = {"model": args.model,
              "ran_at": datetime.now(timezone.utc).replace(microsecond=0)
                        .isoformat(),
              "fills": {}}
    filled = 0
    cost = 0.0
    dirty: set[Path] = set()
    cache: dict[Path, list] = {}

    for start in range(0, len(todo), _BATCH):
        batch = todo[start:start + _BATCH]
        lines = []
        for j, (p, _, r) in enumerate(batch, 1):
            name = r.get("company_name") or r.get("name")
            firm = p.name[: -len("_companies.json")]
            dom = _domain(r)
            lines.append(f"{j}. {name}" + (f" — {dom}" if dom else "")
                         + f" (portfolio of {firm})")
        prompt = _PROMPT.format(taxonomy=taxonomy, companies="\n".join(lines))
        try:
            text, usage = _call(args.model, prompt)
        except Exception as exc:  # noqa: BLE001 — keep what we have, stop clean
            print(f"[tag-backfill] API error, stopping (progress kept): {exc}")
            break
        cost += budget.record(bstate, "tag-backfill", args.model, usage)
        answers = parse_reply(text, len(batch))
        for j, (p, i, _) in enumerate(batch, 1):
            got = answers.get(j) or []
            if not got:
                continue
            recs = cache.setdefault(p, json.loads(p.read_text()))
            if recs[i].get("everywhere_tags"):
                continue                      # something else tagged it: wins
            recs[i]["everywhere_tags"] = got
            name = recs[i].get("company_name") or recs[i].get("name")
            report["fills"].setdefault(p.name, {})[name] = got
            filled += 1
            dirty.add(p)
        done = min(start + _BATCH, len(todo))
        print(f"[tag-backfill] {done}/{len(todo)} classified, "
              f"{filled} tagged, ${cost:.4f}", flush=True)
        time.sleep(0.3)

    for p in sorted(dirty):
        p.write_text(json.dumps(cache[p], indent=2, ensure_ascii=False) + "\n")
    report["companies_tagged"] = filled
    report["cost_usd"] = round(cost, 4)
    _REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    budget.save(bstate)
    print(f"\n[tag-backfill] tagged {filled} companies in {len(dirty)} files "
          f"for ${cost:.4f}; report -> data/llm_tag_report.json")
    if dirty:
        print("next:  git add data/ && git commit -m 'LLM tag backfill "
              f"({filled} companies)' && git push origin main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
