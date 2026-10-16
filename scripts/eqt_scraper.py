#!/usr/bin/env python3
"""EQT (EQT Group, incl. EQT Ventures, EQT Growth, EQT Life Sciences, BPEA EQT,
Infrastructure and Private Capital funds) current-portfolio scraper -> eqt_companies.json
Source: https://eqtgroup.com/about/current-portfolio — Next.js App Router page; the
RSC flight payload embeds each company card: name, keyFacts (country, launch year,
sector, exit) and the EQT fund(s) holding it. Descriptions/websites are not in the
list payload.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response
from _d50_common import rec, finish

SOURCE_URL = "https://eqtgroup.com/about/current-portfolio"
PRIMARY = "EQT"
SECTOR_MAP = {"life sciences": ["BioTech", "Health"], "healthcare": ["Health"], "health": ["Health"], "biotech": ["BioTech"],
              "health tech": ["Health"], "energy & environmental": ["Climate / Sustainability"], "climate": ["Climate / Sustainability"],
              "sustainability": ["Climate / Sustainability"], "fintech": ["FinTech / Insurance"],
              "transport & logistics": ["Transportation / Mobility", "Logistics / Supply Chain"], "hr tech": ["Future of Work"],
              "remote work": ["Future of Work"], "consumer": ["Consumer"], "software development": ["Dev Tools / Cloud"],
              "industrial technology": ["Deeptech / Robotics / AR/VR"]}


def fund_title(item):
    d = lambda x: x if isinstance(x, dict) else {}
    route = d(d(item).get("route"))
    path = d(route.get("internalSlugFullPath"))
    if isinstance(path.get("title"), str) and path["title"]:
        return path["title"]
    slug = d(route.get("internalSlug")).get("current")
    return pretty(slug) if isinstance(slug, str) else None


def pretty(slug):
    up = {"eqt", "lsp", "bpea", "hef", "he"}
    roman = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}
    return " ".join(w.upper() if w in up or w in roman else w.capitalize() for w in re.split(r"[-_ ]+", slug) if w)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch_response(SOURCE_URL).content.decode("utf-8")
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    flight = "".join(json.loads('"' + c + '"') for c in chunks)
    dec, objs = json.JSONDecoder(), {}
    for m in re.finditer(r'\{"_id":"[0-9a-f-]+","_key":null,"keyFacts"', flight):
        try:
            o, _ = dec.raw_decode(flight, m.start())
        except ValueError:
            continue
        if o.get("title"):
            objs.setdefault(o["_id"], o)
    out = []
    for o in objs.values():
        kf = o.get("keyFacts") or {}
        funds = [f for f in (fund_title(i) for i in kf.get("fundItems") or []) if f]
        if not funds:
            funds = [pretty(f) for f in o.get("formatedFunds") or []]
        slug = (o.get("slug") or {}).get("current")
        ly = kf.get("launchYear")
        out.append(rec(o["title"], None, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[kf["sector"]] if kf.get("sector") else None, sector_map=SECTOR_MAP,
                       location=kf.get("country"), fund=", ".join(dict.fromkeys(funds)) or None,
                       launch_year=int(ly) if str(ly or "").isdigit() else None,
                       status="exited" if kf.get("exit") else "active",
                       detail_url=f"{SOURCE_URL}/{slug}" if slug else None))
    finish(out, "eqt", ("location", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
