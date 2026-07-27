"""Guard for machine-generated scrapers — the checks that replace human review.

Three independent layers; ALL must pass before a generated scraper is committed:

1. static_check(code)  — AST allowlist. Rejects env access, subprocess, eval/exec,
   open()/file I/O, sockets, and any import off the whitelist. This blocks the
   "generated code exfiltrates tokens" class outright.
2. run_sandboxed(path) — executes scrape() in a subprocess with a SCRUBBED
   environment (no tokens exist in it even if layer 1 were beaten) and a timeout.
3. validate_output(records, baseline) — the data must look like a real, RICH
   portfolio: enough records vs the generic baseline, near-total names, solid
   URL + description coverage, low duplication. Catches empty, thin, and
   structurally-wrong results. (Honest limit: cannot catch subtly-wrong values.)
"""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

_ALLOWED_IMPORTS = {
    "requests", "bs4", "json", "re", "time", "datetime", "urllib",
    "urllib.parse", "html", "collections", "itertools", "typing",
    "math", "string", "unicodedata",
}
_BANNED_CALLS = {"eval", "exec", "compile", "__import__", "open", "input",
                 "breakpoint", "globals", "locals", "vars", "getattr", "setattr"}
_BANNED_ATTRS = {"environ", "getenv", "putenv", "system", "popen", "spawn",
                 "fork", "socket", "connect_ex"}


def static_check(code: str) -> list[str]:
    """Return a list of violations (empty = pass)."""
    problems: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [f"syntax error: {exc}"]

    has_scrape = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "scrape":
            has_scrape = True
        if isinstance(node, ast.Import):
            for a in node.names:
                root = a.name.split(".")[0]
                if a.name not in _ALLOWED_IMPORTS and root not in _ALLOWED_IMPORTS:
                    problems.append(f"forbidden import: {a.name}")
        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if node.module not in _ALLOWED_IMPORTS and root not in _ALLOWED_IMPORTS:
                problems.append(f"forbidden import-from: {node.module}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in _BANNED_CALLS:
                problems.append(f"forbidden call: {node.func.id}()")
        if isinstance(node, ast.Attribute) and node.attr in _BANNED_ATTRS:
            problems.append(f"forbidden attribute: .{node.attr}")
        if isinstance(node, (ast.Global, ast.Nonlocal)):
            problems.append("forbidden global/nonlocal")
    if not has_scrape:
        problems.append("no scrape() function defined")
    return sorted(set(problems))


def run_sandboxed(candidate_path: str, timeout: int | None = None) -> tuple[list | None, str]:
    """Execute the candidate's scrape() with NO credentials in the environment.
    Returns (records, "") or (None, reason)."""
    runner = str(Path(__file__).resolve().parent / "scraper_runner.py")
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin", "LANG": "C.UTF-8",
           "HOME": "/tmp", "PYTHONDONTWRITEBYTECODE": "1"}   # deliberately NO tokens
    try:
        proc = subprocess.run(
            [sys.executable, runner, candidate_path],
            capture_output=True, text=True, env=env,
            timeout=timeout or int(os.environ.get("GEN_RUN_TIMEOUT", "420")),
        )
    except subprocess.TimeoutExpired:
        return None, "sandbox timeout"
    if proc.returncode != 0:
        return None, f"sandbox exit {proc.returncode}: {proc.stderr.strip()[-400:]}"
    try:
        records = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None, "sandbox produced non-JSON output"
    return (records, "") if isinstance(records, list) else (None, "not a list")


def validate_output(records: list, baseline_count: int = 0) -> list[str]:
    """Return a list of failures (empty = pass). `baseline_count` is what the
    generic extractor found for this site (0 if it found nothing)."""
    fails: list[str] = []
    n = len(records)
    if n < 10:
        fails.append(f"too few records ({n})")
    if baseline_count and n < 0.5 * baseline_count:
        fails.append(f"count {n} < 50% of generic baseline {baseline_count}")
    if any(not isinstance(r, dict) for r in records):
        return fails + ["non-dict records"]

    def cov(key_alts: tuple[str, ...]) -> float:
        hit = sum(1 for r in records
                  if any(r.get(k) not in (None, "", []) for k in key_alts))
        return hit / n if n else 0.0

    names = [str(r.get("company_name") or r.get("name") or "").strip() for r in records]
    if sum(1 for x in names if x) < 0.95 * n:
        fails.append("names missing on >5% of records")
    if n and len({x.lower() for x in names if x}) < 0.7 * n:
        fails.append("heavy duplication in names")
    if cov(("company_url", "url", "website")) < 0.6:
        fails.append("company_url coverage < 60%")
    if cov(("description", "tagline", "summary")) < 0.3:
        fails.append("description coverage < 30% (not rich)")

    # type integrity: a string value that PARSES as a list/dict is a stringified
    # structure ("['A', 'B']") — a real field the model flattened. Feeding the
    # field names back makes the next burst try fix it.
    bad_fields: set[str] = set()
    for r in records:
        for k, v in r.items():
            if not isinstance(v, str):
                continue
            s = v.strip()
            if len(s) < 2 or s[0] not in "[{" or s[-1] not in "]}":
                continue
            try:
                parsed = ast.literal_eval(s)
            except (ValueError, SyntaxError):
                try:
                    parsed = json.loads(s)
                except json.JSONDecodeError:
                    continue
            if isinstance(parsed, (list, dict)):
                bad_fields.add(k)
    if bad_fields:
        fails.append("stringified list/dict in field(s): "
                     + ", ".join(sorted(bad_fields)[:4]))
    return fails
