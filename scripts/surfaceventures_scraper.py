#!/usr/bin/env python3
"""Surface Ventures portfolio scraper -> surfaceventures_companies.json
Source: https://surfacevc.com/portfolio — the Angular portfolio page's own company list (a data
array shipped in the site's JS bundle, the same records the cards render): company name,
location, Surface's sector tags, status (Active / Exited …), description and website."""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://surfacevc.com/portfolio"
ORIGIN = "https://surfacevc.com/"
PRIMARY = "Surface Ventures"


def records():
    home = fetch(ORIGIN)
    seen, queue = set(), re.findall(r'src="((?:main|chunk)-[A-Z0-9]+\.js)"', home)
    while queue:
        js = queue.pop(0)
        if js in seen:
            continue
        seen.add(js)
        t = fetch(ORIGIN + js)
        queue += [c for c in re.findall(r"(chunk-[A-Z0-9]+\.js)", t) if c not in seen]
        m = re.search(r"=\s*(\[\{CompanyName:.*?\}\])\s*[,;]", t, re.S)
        if m:
            lit = re.sub(r'([{,])\s*([A-Za-z_]\w*)\s*:', r'\1"\2":', m.group(1))
            return json.loads(lit)
    raise SystemExit("FATAL: Surface company list not found in site bundle")


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for x in records():
        name = clean(x.get("CompanyName"))
        if not name:
            continue
        url = clean(x.get("Website"))
        if url and is_social(url):
            url = None
        st = clean(x.get("Status"))
        out.append(rec(name, x.get("Description"), url, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=x.get("Sectors") or [], location=x.get("Location"),
                       status=st.lower() if st else None))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Surface companies")
    finish(out, "surfaceventures", ("description", "company_url", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
