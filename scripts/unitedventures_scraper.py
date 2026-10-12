#!/usr/bin/env python3
"""United Ventures portfolio scraper -> unitedventures_companies.json
Source: WP REST https://unitedventures.com/wp-json/wp/v2/portfolio — content HTML
carries website, Sector, Founder, and description.
"""
import html as htmlmod
import os, re, sys, time
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (HEADERS, TIMEOUT, clean, tags_for, clean_url,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://unitedventures.com/portfolio/"
API = "https://unitedventures.com/wp-json/wp/v2/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "unitedventures_companies.json")
PRIMARY = "United Ventures"
SECTOR_TAG_MAP = {
    "cybersecurity": ["Cybersecurity"], "fintech": ["FinTech / Insurance"],
    "deeptech": ["Deeptech / Robotics / AR/VR"], "deep tech": ["Deeptech / Robotics / AR/VR"],
    "saas": ["Dev Tools / Cloud"], "health": ["Health"], "climate": ["Climate / Sustainability"],
    "ai": ["Data & Analytics"], "marketplace": ["Consumer"],
}
TAG_OVERRIDES = {}


def fetch_all():
    out, page = [], 1
    while True:
        r = requests.get(API, params={"per_page": 100, "page": page}, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        out.extend(batch)
        total = int(r.headers.get("X-WP-TotalPages") or 1)
        if page >= total:
            break
        page += 1
        time.sleep(0.15)
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for p in fetch_all():
        name = clean(htmlmod.unescape(p.get("title", {}).get("rendered") or ""))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        content = BeautifulSoup(p.get("content", {}).get("rendered") or "", "html.parser")
        text = clean(content.get_text("\n"))
        website = None
        # first line often "Name www.example.com" or bare domain
        for a in content.select("a[href^=http]"):
            u = clean_url(a["href"])
            if u and "unitedventures.com" not in u:
                website = u
                break
        if not website and text:
            m = re.search(r"\b((?:https?://)?(?:www\.)?[a-z0-9.-]+\.[a-z]{2,})(/[^\s]*)?", text, re.I)
            if m and "unitedventures" not in m.group(0).lower():
                website = clean_url(m.group(0) if m.group(0).startswith("http") else "https://" + m.group(0))
        sector = None
        m = re.search(r"Sector\s+([^\n]+)", text or "", re.I)
        if m:
            sector = clean(m.group(1))
        founders = []
        m = re.search(r"Founder[s]?\s+([^\n]+)", text or "", re.I)
        if m:
            founders = [clean(x) for x in re.split(r",| and ", m.group(1)) if clean(x)]
        # description: after founder/sector block
        desc = None
        parts = re.split(r"Founder[s]?\s+[^\n]+", text or "", maxsplit=1, flags=re.I)
        if len(parts) > 1:
            desc = clean(parts[1])
        if not desc:
            # strip leading name/url/sector lines
            lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
            body = []
            for ln in lines:
                if ln.lower().startswith(("sector", "founder")) or ln.lower() == name.lower():
                    continue
                if re.match(r"^(https?://|www\.)", ln, re.I) or re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", ln, re.I):
                    continue
                body.append(ln)
            desc = clean(" ".join(body)) if body else None
        sectors = [sector] if sector else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": sectors,
            "founders": founders or None,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
