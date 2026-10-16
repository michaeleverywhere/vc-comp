#!/usr/bin/env python3
"""Georgian portfolio scraper -> georgian_companies.json
Source: https://georgian.io/portfolio — the Next.js flight payload embedded in
the page carries the full company list (name, summary, description, website,
industries, status).
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://georgian.io/portfolio"
PRIMARY = "Georgian"
SECTOR_MAP = {"cybersecurity": ["Cybersecurity"], "financial services and insurance": ["FinTech / Insurance"],
              "healthcare": ["Health"], "supply chain": ["Logistics / Supply Chain"], "analytics": ["Data & Analytics"],
              "data infrastructure": ["Data & Analytics", "Dev Tools / Cloud"], "developer productivity": ["Dev Tools / Cloud"],
              "education and legal": ["RegTech/Gov/Legal"], "physical ai": ["Deeptech / Robotics / AR/VR"],
              "quantum computing": ["Deeptech / Robotics / AR/VR"], "workforce automation": ["Future of Work"]}


def blocks_text(blocks):
    return clean(" ".join(c.get("text", "") for b in blocks or [] for c in b.get("children") or []))


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html, re.S)
    txt = "".join(json.loads('"' + c + '"') for c in chunks)
    i = txt.index('{"companies":[')
    data, _ = json.JSONDecoder().raw_decode(txt[i:])
    out = []
    for c in data["companies"]:
        site = c.get("companyUrl") or next((l.get("url") for l in c.get("links") or [] if l.get("type") == "website"), None)
        st = (c.get("status") or "").lower() or None
        out.append(rec(c.get("name"), blocks_text(c.get("descriptionBlocks") or c.get("description")) or c.get("summary"), site,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[x.get("title") for x in c.get("industries") or []],
                       sector_map=SECTOR_MAP, summary=c.get("summary"), status=st))
    finish(out, "georgian", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
