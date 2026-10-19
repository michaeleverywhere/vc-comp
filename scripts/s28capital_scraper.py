#!/usr/bin/env python3
"""S28 Capital portfolio scraper -> s28capital_companies.json
Source: https://www.s28capital.com/ — the site's own public Prismic content API
(s28capital.cdn.prismic.io, "company" documents that build the portfolio page): company name,
description, founders (name + title) and website; plus the home-page portfolio grid
("front_page" document): the one-line excerpt (-> tagline) and the "Exited" flag (-> status)."""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.s28capital.com/"
API = "https://s28capital.cdn.prismic.io/api/v2"
PRIMARY = "S28 Capital"


def txt(v):
    return clean(" ".join(b.get("text") or "" for b in (v or []) if isinstance(b, dict))) if isinstance(v, list) else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    ref = next(r["ref"] for r in fetch(API, as_json=True)["refs"] if r.get("isMasterRef"))
    docs, page = [], 1
    while True:
        q = quote('[[at(document.type,"company")]]')
        j = fetch(f"{API}/documents/search?ref={ref}&q={q}&pageSize=100&page={page}", as_json=True)
        docs += j["results"]
        if page >= j.get("total_pages", 1):
            break
        page += 1
    exited, tagline = {}, {}
    q = quote('[[at(document.type,"front_page")]]')
    for fp in fetch(f"{API}/documents/search?ref={ref}&q={q}", as_json=True)["results"]:
        for sl in fp["data"].get("body") or []:
            pr = sl.get("primary") or {}
            lid = (pr.get("link") or {}).get("id")
            if lid:
                exited[lid] = str(pr.get("exited")).lower() == "true"
                tagline[lid] = txt(pr.get("excerpt"))
    out = []
    for d in docs:
        x = d["data"]
        name = txt(x.get("title"))
        paras = [b.get("text") for b in (x.get("content") or []) if b.get("type") == "paragraph" and clean(b.get("text"))]
        founders = []
        for f in x.get("founders") or []:
            fn, ft = txt(f.get("founder_name")), txt(f.get("founder_title"))
            if fn:
                founders.append(f"{fn} ({ft})" if ft else fn)
        url = (x.get("link") or {}).get("url")
        status = "Exited" if exited.get(d["id"]) else None
        out.append(rec(name, " ".join(paras) or None, url if url and not is_social(url) else None,
                       PRIMARY, SOURCE_URL, scraped_at, tagline=tagline.get(d["id"]), founders=founders, status=status))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} S28 companies")
    finish(out, "s28capital", ("description", "tagline", "company_url", "founders", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
