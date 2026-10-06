"""Y Combinator: every company in ycombinator.com/companies (all batches).

Source: the public Algolia search index behind ycombinator.com/companies (app id
+ search-only key are embedded in that page as window.AlgoliaOpts), queried one
batch at a time to get past the 1000-hit pagination cap. Founders come from each
company's public YC page (ycombinator.com/companies/<slug>, data-page JSON).
"""
import html as _html
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from common import UA, clean, dedupe, save, tag

BASE = "https://www.ycombinator.com/companies"
SEASON = {"Winter": "W", "Summer": "S", "Spring": "X", "Fall": "F"}


def batch_label(b):
    m = re.match(r"(Winter|Summer|Spring|Fall) (\d{4})", b or "")
    return f"YC {SEASON[m.group(1)]}{m.group(2)[2:]}" if m else (f"YC {b}" if b and b != "Unspecified" else "YC")


def algolia():
    page = requests.get(BASE, headers=UA, timeout=30).text
    o = json.loads(re.search(r"window.AlgoliaOpts = (\{.*?\})", page).group(1))
    url = f"https://{o['app'].lower()}-dsn.algolia.net/1/indexes/*/queries"
    h = {"x-algolia-application-id": o["app"], "x-algolia-api-key": o["key"]}

    def q(params):
        r = requests.post(url, headers=h, json={"requests": [
            {"indexName": "YCCompany_production", "params": params}]}, timeout=60)
        r.raise_for_status()
        return r.json()["results"][0]
    return q


def founders(slug):
    for attempt in range(3):
        try:
            r = requests.get(f"{BASE}/{slug}", headers=UA, timeout=30)
            if r.status_code == 404:
                return None
            m = re.search(r'data-page="([^"]+)"', r.text)
            if not m:
                time.sleep(2)
                continue
            c = json.loads(_html.unescape(m.group(1)))["props"]["company"]
            fs = [clean(f.get("full_name")) for f in (c.get("founders") or []) if f.get("full_name")]
            return fs
        except Exception:
            time.sleep(2 + attempt * 3)
    return None


def main(limit=None):
    q = algolia()
    from urllib.parse import quote
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
    print(f"[yc] algolia hits {len(hits)} (facet total {sum(facets.values())})")
    if limit:
        hits = hits[:limit]
    with ThreadPoolExecutor(8) as ex:
        fl = list(ex.map(lambda h: founders(h["slug"]), hits))
    recs = []
    for h, fs in zip(hits, fl):
        labels = [x for x in (h.get("industries") or [])] + (h.get("tags") or [])
        desc = clean(h.get("one_liner"))
        long = clean(h.get("long_description"))
        if long and long.lower() != desc.lower():
            desc = f"{desc} {long}".strip() if desc else long
        verticals = "; ".join(dict.fromkeys(
            [clean(h.get("subindustry") or h.get("industry"))] + (h.get("tags") or [])))
        recs.append({
            "name": clean(h["name"]),
            "description": desc,
            "website": clean(h.get("website")),
            "team": ", ".join(fs or []),
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
            "founders_fetched": fs is not None,
        })
    recs = dedupe(recs)
    save("ycombinator", recs, {"source": "https://www.ycombinator.com/companies",
                               "method": "Algolia public index + company pages"})


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else None)
