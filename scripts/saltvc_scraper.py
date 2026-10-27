#!/usr/bin/env python3
"""Salt VC portfolio scraper -> saltvc_companies.json
Source: https://salt.vc (chrome-dom); formerly Peterson Ventures. Cards labelled Portfolio Company."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://salt.vc"
PRIMARY = "Salt VC"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    html = dom(SOURCE_URL, 20000, min_len=10000)
    s = BeautifulSoup(html, "html.parser")
    for t in s(["script", "style", "noscript"]):
        t.decompose()
    seen = set()
    # Prefer structured "Portfolio Company NAME Industry ..." blocks
    for div in s.find_all("div"):
        # only leaf-ish blocks that start with Portfolio Company
        kids = [c for c in div.children if getattr(c, "name", None)]
        texts = [clean(c.get_text(" ", strip=True)) for c in kids]
        texts = [t for t in texts if t]
        if not texts:
            continue
        # look for a child that is exactly "Portfolio Company X" or starts with it
        for i, t in enumerate(texts):
            m = re.match(r"^Portfolio Company\s+(.+)$", t)
            if not m:
                continue
            nm = clean(m.group(1))
            if not nm or len(nm) > 50 or nm.lower() in seen:
                continue
            seen.add(nm.lower())
            industry = None
            for t2 in texts[i + 1 : i + 6]:
                m2 = re.match(r"^Industry\s+(.+)$", t2)
                if m2:
                    industry = clean(m2.group(1))
                    break
            sectors = [s.strip() for s in re.split(r"[,/]", industry)] if industry else None
            sectors = [x for x in (sectors or []) if x][:4] or None
            out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors))
            break
    # fallback regex over full text
    if len(out) < 5:
        full = s.get_text("\n", strip=True)
        for m in re.finditer(r"Portfolio Company\s+([A-Za-z0-9][A-Za-z0-9 .&\-]{1,40})\s+Industry\s+([^\n]+)", full):
            nm = clean(m.group(1))
            if not nm or nm.lower() in seen:
                continue
            seen.add(nm.lower())
            industry = clean(m.group(2))
            sectors = [x.strip() for x in re.split(r"[,/]", industry or "")][:4] or None
            out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors))
    finish(out, "saltvc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
