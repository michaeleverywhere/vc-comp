"""SOSV (+ HAX and IndieBio, deduped against SOSV).

Sources: the public WordPress REST API behind sosv.com/portfolio (post type
`company`, taxonomies tx_cohort / tx_program / tx_stage / tx_category, ACF fields
tagline, total_capital_raised, demo_day_* from SOSV demo-day pages) and the
`founder` post type (linked to companies through tx_company). hax.co/startups runs
the same stack; HAX-only companies not already in SOSV's portfolio are added.
IndieBio (renamed SOSV NY / SOSV SF in 2024) is a program inside SOSV's portfolio.
Outputs sosv_companies.json (the Airtable set) plus hax_/indiebio_ subsets.
"""
import html
import re
import time

import requests

from common import UA, clean, dedupe, norm_name, save, tag

STAGE_TO_ROUND = {"Pre-Seed": "Pre-Seed", "Seed": "Seed", "Series A(+)": "Series A",
                  "Series A": "Series A", "Series B": "Series B", "Growth": "Growth"}
HAX_PROGRAMS = {"HAX", "SOSV HAX"}
INDIEBIO_PROGRAMS = {"IndieBio", "IndieBio NY", "IndieBio SF", "SOSV NY", "SOSV SF"}


def get_all(base, path, params=None):
    out, page = [], 1
    while True:
        p = {"per_page": 100, "page": page, **(params or {})}
        for attempt in range(4):
            r = requests.get(f"{base}/wp-json/wp/v2/{path}", params=p, headers=UA, timeout=60)
            if r.status_code < 500:
                break
            time.sleep(3 * (attempt + 1))
        if r.status_code == 400:
            break
        r.raise_for_status()
        d = r.json()
        out += d
        if page >= int(r.headers.get("X-WP-TotalPages", 1)):
            break
        page += 1
    return out


def txt(h):
    return clean(html.unescape(re.sub(r"<[^>]+>", " ", h or "")))


def terms(base, tax):
    return {t["id"]: html.unescape(t["name"]) for t in get_all(base, tax)}


def scrape_site(base, label):
    comps = get_all(base, "company")
    tx = {t: terms(base, t) for t in ["tx_cohort", "tx_program", "tx_stage", "tx_category", "tx_company"]}
    founders = {}
    try:
        for f in get_all(base, "founder"):
            pos = clean((f.get("acf") or {}).get("position"))
            name = txt(f["title"]["rendered"])
            if pos and not re.search(r"found|ceo|cto|coo|chief exec", pos, re.I):
                continue
            for cid in f.get("tx_company") or []:
                founders.setdefault(cid, []).append(name)
    except requests.HTTPError:
        pass
    recs = []
    for c in comps:
        a = c.get("acf") or {}
        name = txt(c["title"]["rendered"])
        cohorts = [tx["tx_cohort"].get(i, "") for i in c.get("tx_cohort") or []]
        progs = [tx["tx_program"].get(i, "") for i in c.get("tx_program") or []]
        stages = [tx["tx_stage"].get(i, "") for i in c.get("tx_stage") or []]
        cats = [tx["tx_category"].get(i, "") for i in c.get("tx_category") or []]
        tagline = clean(html.unescape(a.get("tagline") or ""))
        body = txt((c.get("content") or {}).get("rendered")) or txt(a.get("demo_day_description"))
        desc = tagline if not body else (f"{tagline} {body}" if tagline and tagline not in body else body)
        amt = clean(a.get("total_capital_raised"))
        dil = clean(a.get("demo_day_dilutive_funding"))
        if not amt and dil and dil not in ("$0", "0"):
            amt = dil
        rnd = next((STAGE_TO_ROUND[s] for s in stages if s in STAGE_TO_ROUND), "")
        team = []
        for cid in c.get("tx_company") or []:
            team += founders.get(cid, [])
        dd_tags = [clean(t) for t in (a.get("demo_day_tags") or "").split(",") if clean(t)]
        recs.append({
            "name": name, "description": desc, "website": clean(a.get("website")),
            "team": ", ".join(dict.fromkeys(team)), "round": rnd, "amount_raised": amt,
            "date": "; ".join(f"SOSV {x}" if not x.lower().startswith(("sosv", "hax", "indiebio")) else x
                              for x in cohorts if x),
            "verticals": "; ".join(dict.fromkeys(cats + dd_tags)),
            "programs": [p for p in progs if p], "stage": "; ".join(stages),
            "founded_year": clean(a.get("founded_year")),
            "everywhere_tags": tag(name, tagline or body, cats),
            "source_url": c.get("link"), "site": label,
        })
    return recs


def main():
    sosv = scrape_site("https://sosv.com", "sosv.com")
    hax = scrape_site("https://hax.co", "hax.co")
    print(f"[sosv] sosv.com {len(sosv)}  hax.co {len(hax)}")
    keys = {norm_name(r["name"]) for r in sosv}
    hax_only = [r for r in hax if norm_name(r["name"]) not in keys]
    # enrich SOSV rows with HAX-site fields where SOSV left them blank
    hx = {norm_name(r["name"]): r for r in hax}
    for r in sosv:
        h = hx.get(norm_name(r["name"]))
        if h:
            for f in ("description", "team", "round", "amount_raised", "verticals", "website", "date"):
                if not r.get(f) and h.get(f):
                    r[f] = h[f]
    for r in hax_only:
        r["programs"] = list(dict.fromkeys(r["programs"] + ["HAX"]))
    allr = sosv + hax_only
    for r in allr:
        ps = set(r["programs"])
        sub = "HAX" if ps & HAX_PROGRAMS else ("IndieBio" if ps & INDIEBIO_PROGRAMS else "")
        r["investors"] = f"SOSV ({sub})" if sub else "SOSV"
        r["source"] = "SOSV"
    allr = dedupe(allr)
    save("sosv", allr, {"source": "https://sosv.com/portfolio/ + https://hax.co/startups/",
                        "method": "WordPress REST API (company + founder post types)",
                        "hax_only_added": len(hax_only)})
    save("hax", [r for r in allr if r["investors"] == "SOSV (HAX)"],
         {"note": "subset of sosv_companies.json; Airtable rows come from SOSV set"})
    save("indiebio", [r for r in allr if r["investors"] == "SOSV (IndieBio)"],
         {"note": "subset of sosv_companies.json; IndieBio = SOSV NY/SF since 2024"})


if __name__ == "__main__":
    main()
