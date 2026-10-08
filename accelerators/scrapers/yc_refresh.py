"""Smart YC refresh: Algolia full pull + selective founder page fetches.

Reuses yc.py Algolia + founders helpers. Only hits company pages for NEW
slugs or records whose team is empty and founders_fetched is not True.
"""
from __future__ import annotations

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

from common import DATA_DIR, clean, dedupe, norm_name, save, tag
from yc import BASE, algolia, batch_label, founders

SLUG_RE = re.compile(r"/companies/([^/?#]+)")


def slug_of(rec_or_url):
    if isinstance(rec_or_url, dict):
        u = rec_or_url.get("source_url") or ""
    else:
        u = rec_or_url or ""
    m = SLUG_RE.search(u)
    return m.group(1) if m else ""


def hit_to_partial(h):
    labels = list(h.get("industries") or []) + list(h.get("tags") or [])
    desc = clean(h.get("one_liner"))
    long = clean(h.get("long_description"))
    if long and long.lower() != desc.lower():
        desc = f"{desc} {long}".strip() if desc else long
    verticals = "; ".join(dict.fromkeys(
        [clean(h.get("subindustry") or h.get("industry"))] + (h.get("tags") or [])))
    return {
        "name": clean(h["name"]),
        "description": desc,
        "website": clean(h.get("website")),
        "linkedin_url": "",
        "team": "",
        "round": "",
        "amount_raised": "",
        "date": batch_label(h.get("batch")),
        "verticals": verticals.strip("; "),
        "investors": "Y Combinator",
        "source": "YC",
        "everywhere_tags": (tag(h["name"], h.get("one_liner") or "", labels)
                            or tag(h["name"], long)[:2]),
        "status": clean(h.get("status")),
        "location": clean(h.get("all_locations")),
        "source_url": f"{BASE}/{h['slug']}",
        "founders_fetched": False,
        "_slug": h["slug"],
    }


def pull_hits():
    q = algolia()
    facets = q("query=&hitsPerPage=0&facets=%5B%22batch%22%5D&maxValuesPerFacet=1000")["facets"]["batch"]
    hits = []
    for b in facets:
        page = 0
        while True:
            ff = quote(json.dumps([[f"batch:{b}"]]))
            res = q(f"query=&hitsPerPage=1000&page={page}&facetFilters={ff}")
            hits += res["hits"]
            page += 1
            if page >= res["nbPages"]:
                break
    print(f"[yc_refresh] algolia hits {len(hits)} (facet total {sum(facets.values())})")
    print(f"[yc_refresh] batch facets: {sorted(facets.keys())[-12:]}")
    return hits, facets


def merge(old_by_slug, old_by_name, partial):
    """Prefer fresh Algolia for description/status/location/batch/verticals/tags;
    carry forward team/linkedin/website/enrichment from old when useful."""
    slug = partial["_slug"]
    old = old_by_slug.get(slug) or old_by_name.get(norm_name(partial["name"]))
    rec = {k: v for k, v in partial.items() if k != "_slug"}
    if not old:
        return rec, True  # new
    # carry forward
    if old.get("team"):
        rec["team"] = old["team"]
    if old.get("linkedin_url"):
        rec["linkedin_url"] = old["linkedin_url"]
    if not rec.get("website") and old.get("website"):
        rec["website"] = old["website"]
    # preserve enrichment flags / batch fields (recomputed later) and financing if any
    for k in ("founders_fetched", "description_source", "linkedin_source",
              "round", "amount_raised", "batch_date", "batch_date_precision",
              "most_recent_batch"):
        if old.get(k) not in (None, "") and k not in ("batch_date", "batch_date_precision", "most_recent_batch"):
            if k == "founders_fetched":
                rec["founders_fetched"] = bool(old.get("founders_fetched")) and bool(rec.get("team") or old.get("team"))
            elif k not in rec or not rec.get(k):
                rec[k] = old[k]
    # if we carried team, mark fetched
    if rec.get("team"):
        rec["founders_fetched"] = True
    elif old.get("founders_fetched"):
        rec["founders_fetched"] = True  # already tried; don't re-hit unless new
    return rec, False


def needs_founder_fetch(rec, is_new):
    if is_new:
        return True
    if rec.get("team"):
        return False
    if rec.get("founders_fetched") is True:
        return False
    return True


def main():
    path = os.path.join(DATA_DIR, "ycombinator_companies.json")
    old_payload = json.load(open(path))
    old_companies = old_payload["companies"]
    old_count = len(old_companies)
    old_by_slug = {}
    old_by_name = {}
    for c in old_companies:
        s = slug_of(c)
        if s:
            old_by_slug[s] = c
        old_by_name[norm_name(c.get("name"))] = c
    old_slugs = set(old_by_slug)

    hits, facets = pull_hits()
    partials = [hit_to_partial(h) for h in hits if h.get("slug") and h.get("name")]

    merged = []
    new_flags = []
    for p in partials:
        rec, is_new = merge(old_by_slug, old_by_name, p)
        merged.append(rec)
        new_flags.append(is_new)

    todo_idx = [i for i, (r, n) in enumerate(zip(merged, new_flags)) if needs_founder_fetch(r, n)]
    print(f"[yc_refresh] old={old_count} algolia_partials={len(partials)} "
          f"new={sum(new_flags)} founder_fetches_planned={len(todo_idx)}")

    fetched = 0
    failed = 0

    def fetch_one(i):
        slug = slug_of(merged[i])
        return i, slug, founders(slug)

    with ThreadPoolExecutor(8) as ex:
        futs = [ex.submit(fetch_one, i) for i in todo_idx]
        for fut in as_completed(futs):
            i, slug, info = fut.result()
            fetched += 1
            if info is None:
                failed += 1
                merged[i]["founders_fetched"] = True  # attempted
                continue
            fs = info.get("founders") or []
            if fs:
                merged[i]["team"] = ", ".join(fs)
            if info.get("linkedin_url") and not merged[i].get("linkedin_url"):
                merged[i]["linkedin_url"] = info["linkedin_url"]
            if info.get("website") and not merged[i].get("website"):
                merged[i]["website"] = clean(info["website"])
            merged[i]["founders_fetched"] = True
            if fetched % 25 == 0 or fetched == len(todo_idx):
                print(f"[yc_refresh] founder progress {fetched}/{len(todo_idx)} (failed {failed})")

    # drop helper / ensure no _slug
    for r in merged:
        r.pop("_slug", None)

    before_dedupe = len(merged)
    recs = dedupe(merged)
    new_slugs = {slug_of(r) for r in recs} - old_slugs
    removed_slugs = old_slugs - {slug_of(r) for r in recs if slug_of(r)}
    added_names = sorted({r["name"] for r in recs if slug_of(r) in new_slugs})

    # newest batch labels from Algolia facets (raw) and from records
    from collections import Counter
    batch_counts = Counter(r.get("date") for r in recs if r.get("date") and ";" not in (r.get("date") or ""))
    print(f"[yc_refresh] top date labels: {batch_counts.most_common(12)}")

    save("ycombinator", recs, {
        "source": "https://www.ycombinator.com/companies",
        "method": "Algolia public index + selective company pages (smart refresh)",
    })

    print("--- STATS ---")
    print(f"old_count: {old_count}")
    print(f"new_count: {len(recs)}")
    print(f"before_dedupe: {before_dedupe}")
    print(f"added: {len(added_names)}")
    print(f"added_names: {added_names[:30]}")
    print(f"removed_count: {len(removed_slugs)}")
    print(f"removed_slugs_sample: {sorted(removed_slugs)[:20]}")
    print(f"founder_fetches: {fetched} failed={failed}")
    print(f"newest_batch_labels_seen: {[k for k,_ in batch_counts.most_common(8)]}")
    # facet newest seasons
    print(f"algolia_facet_batches_sample: {sorted(facets.keys())[-15:]}")


if __name__ == "__main__":
    main()
