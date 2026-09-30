#!/usr/bin/env python3
"""Focused Wikidata backfill of empty sectors (+ optional founders/year) only."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enrich as E

FILES = [
    "companies.json", "menlo_companies.json", "trueventures_companies.json",
    "uncork_companies.json", "gradientventures_companies.json", "afore_companies.json",
    "foundrygroup_companies.json", "meritech_companies.json", "a16z_companies.json",
    "usv_companies.json", "index_companies.json", "floodgate_companies.json",
]

def empty(v):
    if v is None: return True
    if isinstance(v, str): return not v.strip()
    if isinstance(v, list): return len(v)==0
    return False

def main():
    report = []
    for fname in FILES:
        path = os.path.join(E.DATA_DIR, fname)
        if not os.path.exists(path):
            continue
        data = json.load(open(path))
        pending = []
        label_ids = []
        scanned = 0
        for o in data:
            if "sectors" not in o or not empty(o.get("sectors")):
                # still allow founders/year if empty
                need = (
                    ("founders" in o and empty(o.get("founders")))
                    or ("year_founded" in o and empty(o.get("year_founded")))
                    or ("founded_year" in o and empty(o.get("founded_year")))
                    or ("ticker_symbol" in o and empty(o.get("ticker_symbol")))
                )
                if not need:
                    continue
            dom = E.domain_of(o.get("company_url"))
            if not dom:
                continue
            name = o.get("company_name") or o.get("name")
            if not name:
                continue
            scanned += 1
            qid, claims = E.wd_match(name, dom)
            time.sleep(0.08)
            if not qid:
                continue
            founders = E.ent_ids(claims, "P112")
            industries = E.ent_ids(claims, "P452")
            exch, tk = E.ticker_pair(claims)
            yr = E.inception_year(claims)
            pending.append(dict(o=o, qid=qid, founders=founders, industries=industries,
                                exch=exch, ticker=tk, year=yr))
            label_ids += founders + industries + ([exch] if exch else [])
        labels = E.get_labels(label_ids)
        n = 0
        for p in pending:
            o, filled = p["o"], {}
            if "founders" in o and empty(o.get("founders")) and p["founders"]:
                names = [labels.get(q) for q in p["founders"] if labels.get(q)]
                if names:
                    o["founders"] = names; filled["founders"] = names
            if "year_founded" in o and empty(o.get("year_founded")) and p["year"]:
                o["year_founded"] = p["year"]; filled["year_founded"] = p["year"]
            if "founded_year" in o and empty(o.get("founded_year")) and p["year"]:
                o["founded_year"] = p["year"]; filled["founded_year"] = p["year"]
            if "sectors" in o and empty(o.get("sectors")) and p["industries"]:
                secs = [labels.get(q) for q in p["industries"]
                        if labels.get(q) and labels[q].lower() not in E.GENERIC_SECTORS]
                if secs:
                    o["sectors"] = secs; filled["sectors"] = secs
            if "ticker_symbol" in o and empty(o.get("ticker_symbol")) and p["ticker"]:
                exch_lbl = labels.get(p["exch"]) or ""
                short = E.EXCH_SHORT.get(exch_lbl, exch_lbl)
                o["ticker_symbol"] = f"{short}: {p['ticker']}".strip(": ").strip()
                filled["ticker_symbol"] = o["ticker_symbol"]
            if not o.get("everywhere_tags"):
                t = E.kw_tags(o.get("company_name"), o.get("description"), o.get("sectors"))
                if t:
                    o["everywhere_tags"] = t; filled["everywhere_tags"] = t
            if filled:
                n += 1
                report.append({"file": fname, "company": o.get("company_name"),
                               "source": "wikidata", "wikidata_id": p["qid"], "filled": filled})
        json.dump(data, open(path, "w"), ensure_ascii=False, indent=2)
        print(f"{fname}: scanned {scanned}, filled {n}", flush=True)

    report_path = os.path.join(E.DATA_DIR, "enrichment_report.json")
    existing = []
    if os.path.exists(report_path):
        try: existing = json.load(open(report_path))
        except Exception: existing = []
    # append (idempotent-ish: keep prior, add new)
    json.dump(existing + report, open(report_path, "w"), ensure_ascii=False, indent=2)
    print(f"TOTAL sector/meta fills this run: {len(report)}", flush=True)

if __name__ == "__main__":
    main()
