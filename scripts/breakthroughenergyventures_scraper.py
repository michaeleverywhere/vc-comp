#!/usr/bin/env python3
"""Breakthrough Energy Ventures portfolio scraper -> breakthroughenergyventures_companies.json
Source: https://www.breakthroughenergy.org/our-work/breakthrough-energy-ventures/bev-portfolio/ — Bill Gates-founded
climate-tech venture fund; the page embeds its Kontent.ai content state (window.__INITIAL_STATE__) holding every BEV
portfolio "company" item: name, the firm's one-line description, website, sector tags (electricity, manufacturing,
agriculture, transportation, buildings) and technology tags."""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.breakthroughenergy.org/our-work/breakthrough-energy-ventures/bev-portfolio/"
PRIMARY = "Breakthrough Energy Ventures"
SECTOR_MAP = {"electricity": ["Climate / Sustainability"], "manufacturing": ["Climate / Sustainability"],
              "agriculture": ["Climate / Sustainability"], "buildings": ["Climate / Sustainability", "PropTech"],
              "transportation": ["Transportation / Mobility", "Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    h = fetch(SOURCE_URL)
    m = re.search(r"window\.__INITIAL_STATE__='(.*?)'</script>", h, re.S)
    if not m:
        raise SystemExit("FATAL: BEV content state not found")
    state = json.loads(re.sub(r"\\(.)", lambda x: x.group(1), m.group(1)))  # JS single-quoted literal -> JSON
    items = {}

    def walk(x):
        if isinstance(x, dict):
            sysd = x.get("system")
            if isinstance(sysd, dict) and sysd.get("type") == "company" and "elements" in x:
                items.setdefault(sysd.get("id"), x)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(state)
    out = []
    for it in items.values():
        e = it["elements"]
        val = lambda k: (e.get(k) or {}).get("value")
        name = clean(val("title")) or clean(it["system"].get("name"))
        if not name:
            continue
        tags = [clean(t.get("name")) for t in val("tags") or [] if clean(t.get("name"))]
        tech = [clean(t.get("name")) for t in val("technologies") or [] if clean(t.get("name"))]
        out.append(rec(name, clean(re.sub(r"<[^>]+>", "", val("description") or "")), clean(val("url")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=tags, sector_map=SECTOR_MAP, technologies=tech))
    if len(out) < 80:
        raise SystemExit(f"FATAL: only {len(out)} BEV companies")
    finish(out, "breakthroughenergyventures", ("description", "company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
