#!/usr/bin/env python3
"""Act One Ventures portfolio scraper -> actone_companies.json
Source: https://www.actoneventures.com/portfolio — Framer page; each company card is a
link to its website containing a category label, the company name (h3), a one-line
description (which carries "Acquired by X." for exits) and an "Acquired" badge. The
nearest preceding h2 gives the portfolio theme (e.g. "Powering Agents")."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.actoneventures.com/portfolio"
PRIMARY = "Act One Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch_response(SOURCE_URL).content.decode("utf-8", "replace"), "html.parser")
    out = []
    for a in s.select("a[href^=http]"):
        h = a.find("h3")
        href = a["href"].strip()
        if not h or "actoneventures" in href or "framer" in href:
            continue
        name = clean(h.get_text(" ", strip=True))
        texts = [(t.parent.name, clean(t)) for t in a.find_all(string=True) if clean(t)]
        idx = next((i for i, (tag, _) in enumerate(texts) if tag == "h3"), 0)
        cat = texts[idx - 1][1] if idx > 0 else None
        after = [t for tag, t in texts[idx + 1:] if tag != "h3"]
        badge = after[-1] if after and after[-1].lower() in ("acquired", "ipo", "exited") else None
        desc = clean(" ".join(after[:-1] if badge else after)) or None
        m = re.search(r"Acquired by ([^.]+)\.", desc or "")
        theme = a.find_previous("h2")
        out.append(rec(name, desc, None if is_social(href) else href, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[cat] if cat else [], category=cat,
                       theme=clean(theme.get_text(" ", strip=True)) if theme else None,
                       acquirer=clean(m.group(1)) if m else None,
                       status=("acquired" if (badge or "").lower() == "acquired" or m else
                               ("public" if (badge or "").lower() == "ipo" else "active"))))
    finish(out, "actone", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
