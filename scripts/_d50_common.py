"""Shared helpers for the 2026-10-16 extra-50 Private Comps batch (additive).

rec()    -> one company record in the house schema (null/[] when absent, tags
            via automation/tags.py keyword classifier only — no LLM).
finish() -> dedupe on lower-cased name, sort, write + coverage print.
"""
import os
from _scraper_common import clean, clean_url, tags_for
from _d20_common import write_out

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data")


def out_path(slug):
    return os.path.join(DATA, f"{slug}_companies.json")


def rec(name, desc, url, primary, source_url, scraped_at, sectors=None, sector_map=None, **extra):
    name, desc = clean(name), clean(desc)
    sectors = [clean(s) for s in (sectors or []) if clean(s)]
    r = {"company_name": name, "description": desc, "company_url": clean_url(url)}
    for k, v in extra.items():
        if isinstance(v, str):
            v = clean(v)
        r[k] = v if v not in ("", None) else ([] if isinstance(v, list) else None)
    if sectors:
        r["sectors"] = sectors
    r["everywhere_tags"] = tags_for(name, desc, sectors, sector_map)
    r["primary_investor"] = primary
    r["source_url"] = source_url
    r["scraped_at"] = scraped_at
    return r


def finish(out, slug, keys=("description", "company_url", "everywhere_tags")):
    seen, res = set(), []
    for r in out:
        n = (r.get("company_name") or "").strip()
        if not n or n.lower() in seen:
            continue
        seen.add(n.lower())
        res.append(r)
    res.sort(key=lambda r: r["company_name"].lower())
    write_out(res, out_path(slug), keys)
    return res
