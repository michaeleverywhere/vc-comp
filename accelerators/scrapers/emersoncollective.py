"""Scrape Emerson Collective public VC portfolio selection.

Source: https://www.emersoncollective.com/our-work/venture-capital
(Next.js __NEXT_DATA__ / Contentful portfolioMatrix). Site presents a selection,
not a complete portfolio. Not a classic accelerator.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from automation.tags import classify  # noqa: E402

URL = "https://www.emersoncollective.com/our-work/venture-capital"
OUT = ROOT / "data" / "accelerators" / "emersoncollective_companies.json"


def rich_text(doc) -> str:
    if not doc:
        return ""
    if isinstance(doc, str):
        return doc.strip()
    parts: list[str] = []

    def walk(n):
        if isinstance(n, dict):
            if n.get("nodeType") == "text":
                parts.append(n.get("value") or "")
            for c in n.get("content") or []:
                walk(c)
        elif isinstance(n, list):
            for c in n:
                walk(c)

    walk(doc)
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def fetch() -> dict:
    req = urllib.request.Request(URL, headers={"User-Agent": "vc-comp-emersoncollective/1.0"})
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if not m:
        raise RuntimeError("no __NEXT_DATA__")
    return json.loads(m.group(1))


def scrape() -> dict:
    data = fetch()
    sections = data["props"]["pageProps"]["data"]["fields"]["items"][0]["fields"]["items"]
    by_name: OrderedDict[str, dict] = OrderedDict()
    for sec in sections:
        sector = (sec["fields"].get("sectionTitle") or "").strip()
        for entry in sec["fields"].get("portfolioMatrix") or []:
            f = entry.get("fields") or {}
            name = (f.get("title") or "").strip()
            if not name:
                continue
            clean = re.sub(r"\s*\((Public|public|Acquired|acquired)\)\s*$", "", name).strip()
            desc = rich_text(f.get("description"))
            ext = (f.get("externalUrl") or "").strip()
            rec = by_name.get(clean) or {
                "name": clean,
                "description": "",
                "sectors": [],
                "website": "",
            }
            if desc and (not rec["description"] or len(desc) > len(rec["description"])):
                rec["description"] = desc
            if ext and not rec["website"]:
                rec["website"] = ext if ext.startswith("http") else ("https://" + ext)
            if sector and sector not in rec["sectors"]:
                rec["sectors"].append(sector)
            by_name[clean] = rec

    companies = []
    for r in by_name.values():
        verticals = "; ".join(r["sectors"])
        companies.append({
            "name": r["name"],
            "description": r["description"],
            "website": r["website"],
            "team": "",
            "round": "",
            "amount_raised": "",
            "date": "",
            "verticals": verticals,
            "investors": "Emerson Collective",
            "source": "Emerson Collective",
            "everywhere_tags": classify(r["name"], r["description"], r["sectors"]),
            "source_url": URL,
            "linkedin_url": "",
            "batch_date": "",
            "batch_date_precision": "",
            "location": "",
            "most_recent_batch": False,
        })
    return {
        "accelerator": "emersoncollective",
        "count": len(companies),
        "source_fn": "emersoncollective",
        "portfolio_url": URL,
        "companies": companies,
    }


if __name__ == "__main__":
    out = scrape()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=2)
    print(OUT, out["count"])
