"""Never-remove merge + guard for company datasets (Michael's standing rule, 2026-10-20:
"NEVER REMOVE ANY COMPANIES JUST SUPPLEMENT AND ADD DATES").

A refresh may only ADD companies and SUPPLEMENT fields. A company the source site no
longer lists is kept with all its data and marked:
    listed_on_site: false, delisted_date: YYYY-MM-DD, last_seen: YYYY-MM-DD (kept)
Companies seen in a scrape get listed_on_site: true and last_seen: <today>; brand-new
ones also get first_seen: <today>. first_seen is never invented for older rows: it is
only set when a company is first added (or derived from git history on a restore).

Works for both dataset shapes:
  * Private Comps  data/<slug>_companies.json            -> JSON list of records
  * Accelerators   data/accelerators/<slug>_companies.json -> {"count", ..., "companies": [...]}

Library:
    merge(old, new, today=None) -> (merged_records, stats)
    missing(old, new)           -> old records with no match in new

CLI (stdlib only; run from the repo root):
    python3 automation/keep_merge.py merge FILE [--base REV] [--date YYYY-MM-DD]
        A scraper just rewrote FILE. Merge the REV (default HEAD) version back in:
        old companies kept (+ delisted dates), new ones added, fields supplemented.
    python3 automation/keep_merge.py check FILE [--base REV]
        Exit 1 (and list them) if FILE drops any company present at REV.
    python3 automation/keep_merge.py guard-staged
        Pre-commit guard (automation/hooks/pre-commit). For every staged, modified
        per-firm / per-accelerator dataset that would drop companies vs HEAD, it
        merges the HEAD companies back into the working file, re-stages it, and
        aborts the commit so masters can be rebuilt before committing again.

Deliberate removals Michael asked for (e.g. Fernbrook Capital), dedupe merges of the
same company, and junk/non-company rows are the only exceptions: run the commit with
ALLOW_COMPANY_REMOVAL=1 and say why in the commit message. Deleting a whole dataset
file (a firm removed on request) is not blocked by the guard.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys
from typing import Optional

NAME_KEYS = ("name", "company_name", "company", "title", "Company Name")
URL_KEYS = ("website", "company_url", "url", "homepage", "Website")
GENERIC_HOSTS = {"linkedin.com", "twitter.com", "x.com", "crunchbase.com", "angel.co",
                 "wellfound.com", "facebook.com", "instagram.com", "github.com",
                 "medium.com", "youtube.com", "bit.ly", "linktr.ee"}
DATE_FIELDS = ("first_seen", "last_seen", "delisted_date", "listed_on_site")


def today_et() -> str:
    try:
        from zoneinfo import ZoneInfo
        return _dt.datetime.now(ZoneInfo("America/New_York")).date().isoformat()
    except Exception:  # noqa: BLE001
        return _dt.date.today().isoformat()


def _first(r: dict, keys) -> str:
    for k in keys:
        v = r.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _domain(u: str) -> str:
    u = (u or "").lower().strip()
    u = re.sub(r"^[a-z]+://", "", u)
    u = re.sub(r"^www\.", "", u)
    return u.split("/")[0].split("?")[0].split("#")[0]


def _keys(r: dict) -> tuple[set, str]:
    names = {_norm(_first(r, NAME_KEYS))}
    if r.get("former_name"):
        names.add(_norm(str(r["former_name"])))
    names.discard("")
    dom = _domain(_first(r, URL_KEYS))
    if dom in GENERIC_HOSTS:
        dom = ""
    return names, dom


def _empty(v) -> bool:
    return v is None or v == "" or v == [] or v == {}


def _index(records: list) -> tuple[dict, dict]:
    by_name, by_dom = {}, {}
    for i, r in enumerate(records):
        if not isinstance(r, dict):
            continue
        names, dom = _keys(r)
        for n in names:
            by_name.setdefault(n, i)
        if dom:
            by_dom.setdefault(dom, i)
    return by_name, by_dom


def _match(r: dict, by_name: dict, by_dom: dict) -> Optional[int]:
    names, dom = _keys(r)
    for n in names:
        if n in by_name:
            return by_name[n]
    if dom and dom in by_dom:
        return by_dom[dom]
    return None


def missing(old: list, new: list) -> list:
    """Old records that have no counterpart (same name/former name or same domain) in new."""
    by_name, by_dom = _index(new)
    return [r for r in old if isinstance(r, dict) and _first(r, NAME_KEYS)
            and _match(r, by_name, by_dom) is None]


def merge(old: list, new: list, today: Optional[str] = None,
          stamp_seen: bool = True) -> tuple[list, dict]:
    """Return (merged, stats). merged = every new record (supplemented with the old
    record's non-empty fields the scrape didn't return) + every old record the scrape
    no longer returned, kept intact and marked delisted. Nothing is ever dropped."""
    today = today or today_et()
    old = [r for r in (old or []) if isinstance(r, dict)]
    new = [r for r in (new or []) if isinstance(r, dict)]
    by_name, by_dom = _index(old)
    used: set = set()
    out: list = []
    st = {"kept_listed": 0, "added": 0, "newly_delisted": 0, "still_delisted": 0,
          "relisted": 0, "fields_supplemented": 0}
    for r in new:
        i = _match(r, by_name, by_dom)
        if i is not None and i in used:
            i = None                      # two scraped rows -> one old row: keep both
        if i is None:
            rec = dict(r)
            if stamp_seen:
                rec.setdefault("first_seen", today)
                rec["last_seen"] = today
                rec["listed_on_site"] = True
            st["added"] += 1
        else:
            used.add(i)
            o = old[i]
            rec = dict(o)
            for k, v in r.items():        # site's current values win when non-empty
                if not _empty(v):
                    rec[k] = v
                elif k not in rec:
                    rec[k] = v
            st["fields_supplemented"] += sum(1 for k, v in r.items()
                                             if not _empty(v) and _empty(o.get(k)))
            if o.get("listed_on_site") is False:
                st["relisted"] += 1
                rec["relisted_date"] = today
                if o.get("delisted_date"):
                    rec["previous_delisted_date"] = o["delisted_date"]
                rec.pop("delisted_date", None)
            else:
                st["kept_listed"] += 1
            if stamp_seen:
                rec["last_seen"] = today
                rec["listed_on_site"] = True
        out.append(rec)
    for i, o in enumerate(old):
        if i in used:
            continue
        rec = dict(o)
        if rec.get("listed_on_site") is False and rec.get("delisted_date"):
            st["still_delisted"] += 1
        else:
            rec["listed_on_site"] = False
            rec["delisted_date"] = today
            st["newly_delisted"] += 1
        out.append(rec)
    assert len(out) >= len(old), "keep_merge invariant broken"
    return out, st


# ---------------------------------------------------------------- file helpers
def _split(doc):
    """(records, rebuild_fn) for either dataset shape."""
    if isinstance(doc, dict) and isinstance(doc.get("companies"), list):
        def rebuild(recs):
            d = dict(doc)
            d["companies"] = recs
            if "count" in d:
                d["count"] = len(recs)
            return d
        return doc["companies"], rebuild
    if isinstance(doc, list):
        return doc, (lambda recs: recs)
    return [], (lambda recs: recs)


def _indent_of(text: str) -> int:
    m = re.search(r"\n( +)\S", text)
    return len(m.group(1)) if m else 2


def _git(*a) -> Optional[str]:
    p = subprocess.run(["git", *a], capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def is_dataset(path: str) -> bool:
    b = os.path.basename(path)
    if not b.endswith("_companies.json"):
        return False
    if b.startswith("all_companies") or b == "all_accelerator_companies.json":
        return False
    return path.startswith("data/") or "/data/" in path


def merge_file(path: str, base: str = "HEAD", today: Optional[str] = None,
               base_text: Optional[str] = None) -> dict:
    base_text = base_text if base_text is not None else _git("show", f"{base}:{path}")
    text = open(path, encoding="utf-8").read()
    if not base_text:
        return {"file": path, "skipped": "no base version"}
    old, _ = _split(json.loads(base_text))
    new, rebuild = _split(json.loads(text))
    merged, st = merge(old, new, today)
    out = json.dumps(rebuild(merged), indent=_indent_of(text), ensure_ascii=False)
    if text.endswith("\n"):
        out += "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(out)
    st.update(file=path, before=len(old), scraped=len(new), after=len(merged))
    return st


def check_file(path: str, base: str = "HEAD", new_text: Optional[str] = None) -> list:
    base_text = _git("show", f"{base}:{path}")
    if not base_text:
        return []
    old, _ = _split(json.loads(base_text))
    new, _ = _split(json.loads(new_text if new_text is not None
                               else open(path, encoding="utf-8").read()))
    return missing(old, new)


def guard_staged() -> int:
    if os.environ.get("ALLOW_COMPANY_REMOVAL") == "1":
        print("[keep_merge] ALLOW_COMPANY_REMOVAL=1 — removal guard skipped "
              "(say why in the commit message)")
        return 0
    staged = (_git("diff", "--cached", "--name-only", "--diff-filter=M") or "").split()
    fixed = []
    for path in staged:
        if not is_dataset(path):
            continue
        staged_text = _git("show", f":{path}")
        try:
            lost = check_file(path, "HEAD", staged_text)
        except Exception as exc:  # noqa: BLE001 — unparsable JSON is someone else's check
            print(f"[keep_merge] {path}: could not parse ({exc}); skipping")
            continue
        if not lost:
            continue
        names = ", ".join(_first(r, NAME_KEYS) for r in lost[:12])
        print(f"[keep_merge] {path}: would drop {len(lost)} companies ({names}"
              f"{' …' if len(lost) > 12 else ''})")
        with open(path, "w", encoding="utf-8") as fh:   # merge onto the STAGED content
            fh.write(staged_text)
        st = merge_file(path, "HEAD")
        subprocess.run(["git", "add", path], check=True)
        fixed.append(st)
    if not fixed:
        return 0
    for st in fixed:
        print(f"[keep_merge] {st['file']}: kept {st['newly_delisted'] + st['still_delisted']} "
              f"no-longer-listed companies (listed_on_site=false, delisted_date set); "
              f"{st['before']} -> {st['after']}")
    print("[keep_merge] Commit ABORTED so nothing is lost. The merged files are staged. "
          "Rebuild the masters (python3 automation/master_builder.py and/or "
          "python3 accelerators/build_combined.py), update counts, then commit again.")
    return 1


def main(argv) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="never-remove merge/guard")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge"); m.add_argument("files", nargs="+")
    m.add_argument("--base", default="HEAD"); m.add_argument("--date")
    c = sub.add_parser("check"); c.add_argument("files", nargs="+")
    c.add_argument("--base", default="HEAD")
    sub.add_parser("guard-staged")
    a = ap.parse_args(argv)
    if a.cmd == "guard-staged":
        return guard_staged()
    rc = 0
    for f in a.files:
        if a.cmd == "merge":
            print(json.dumps(merge_file(f, a.base, a.date)))
        else:
            lost = check_file(f, a.base)
            if lost:
                rc = 1
                print(f"{f}: drops {len(lost)}: " + ", ".join(_first(r, NAME_KEYS) for r in lost))
            else:
                print(f"{f}: ok (no companies dropped vs {a.base})")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
