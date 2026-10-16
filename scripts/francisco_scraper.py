#!/usr/bin/env python3
"""Francisco Partners portfolio scraper -> francisco_companies.json
Source: https://www.franciscopartners.com/investments — Nuxt page; the Apollo
cache inside window.__NUXT__ holds every Investment (name, tile summary, status
Current/Past, sectors, regions, deal scenarios). The __NUXT__ payload is a JS
expression, so it is evaluated with Node in an isolated vm context (data only,
no require/fs/network inside the context).
"""
import json, os, re, subprocess, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

ORIGIN = "https://www.franciscopartners.com"
SOURCE_URL = ORIGIN + "/investments"
PRIMARY = "Francisco Partners"
SECTOR_MAP = {"education technology": ["Future of Work"], "financial technology": ["FinTech / Insurance"],
              "healthcare technology": ["Health"], "healthcare": ["Health"], "security": ["Cybersecurity"],
              "government technology": ["RegTech/Gov/Legal"], "infrastructure software": ["Dev Tools / Cloud"],
              "security & infrastructure": ["Cybersecurity", "Dev Tools / Cloud"], "consumer technology": ["Consumer"],
              "erp & business intelligence": ["Data & Analytics"]}
NODE_JS = ("const vm=require('vm');const src=require('fs').readFileSync(0,'utf8');const ctx={window:{}};"
           "vm.runInNewContext(src,ctx,{timeout:5000});process.stdout.write(JSON.stringify(ctx.window.__NUXT__));")


def nuxt_state(html):
    m = re.search(r"<script>(window\.__NUXT__=.*?)</script>", html, re.S)
    r = subprocess.run(["node", "-e", NODE_JS], input=m.group(1), capture_output=True, text=True, timeout=60, check=True)
    return json.loads(r.stdout)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    state = nuxt_state(fetch_response(SOURCE_URL).content.decode("utf-8"))
    ents = {}

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(k, str) and re.match(r"^(Investment|Sector|Region|Scenario):\d+$", k) and isinstance(v, dict):
                    ents[k] = v.get("value", v) if "value" in v and isinstance(v.get("value"), dict) else v
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(state)
    ref = lambda r: clean((ents.get((r or {}).get("id")) or {}).get("name")) if isinstance(r, dict) else None
    out = []
    for k, v in ents.items():
        if not k.startswith("Investment:") or not clean(v.get("name")):
            continue
        status = clean(v.get("status"))
        sectors = [s for s in (ref(r) for r in v.get("sectors") or []) if s]
        regions = [s for s in (ref(r) for r in v.get("regions") or []) if s]
        scen = [s for s in (ref(r) for r in v.get("scenarios") or []) if s]
        out.append(rec(clean(v["name"]), clean(v.get("tileSummary")) or None, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sectors, sector_map=SECTOR_MAP, region=", ".join(regions) or None,
                       deal_type=", ".join(scen) or None, portfolio_status=status,
                       status={"current": "active", "past": "realized", "former": "realized"}.get((status or "").lower(), (status or "").lower() or None),
                       detail_url=f"{SOURCE_URL}/{v['slug']}" if v.get("slug") else None))
    finish(out, "francisco", ("description", "status", "region", "everywhere_tags"))


if __name__ == "__main__":
    main()
