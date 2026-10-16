#!/usr/bin/env python3
"""Weekend Fund portfolio scraper -> weekend_companies.json
Source: https://weekend.fund/ — homepage cards with name, one-liner, website.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social
from _d20_common import write_out

SOURCE_URL = "https://weekend.fund/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "weekend_companies.json")
PRIMARY = "Weekend Fund"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a[href^=http]"):
        href = a["href"]
        if "weekend.fund" in href or is_social(href):
            continue
        text = clean(a.get_text(" "))
        if not text or len(text) < 3:
            continue
        # "Name One liner..." — first token(s) before description-ish
        # Prefer: name is first capitalized phrase; rest is description
        # Examples: "Alt Marketplace for trading cards", "Deel Global HR..."
        # Use first word/two as name when rest looks like sentence; else whole short string
        name = desc = None
        # If text has known pattern Name + description (description starts lowercase mid)
        parts = text.split(" ", 1)
        if len(text) <= 40 and " " not in text.strip():
            name = text
        else:
            # take leading Proper/Brand tokens until a lowercase function word-heavy phrase
            m = re.match(r"^(.+?)\s+((?:A |An |The |AI |Fast |Global |Digital |An AI|Marketplace|Insights|Find |Everyone|Thermodynamic|AI-powered|AI support).+)$", text)
            if m:
                name, desc = clean(m.group(1)), clean(m.group(2))
            else:
                # fallback: first 1-3 words as name if total long
                words = text.split()
                if len(words) >= 4:
                    name = " ".join(words[:2]) if words[1][0].islower() is False and len(words[0]) < 15 else words[0]
                    # better heuristic: company names rarely > 3 words on this page
                    # Use link structure - often name is first line
                    name = words[0]
                    if len(words) > 1 and words[1][0].isupper() and words[1].lower() not in ("a", "an", "the", "ai", "for"):
                        # two-word name candidates
                        if len(words[1]) < 12:
                            name = words[0] + " " + words[1]
                            desc = clean(" ".join(words[2:])) or None
                        else:
                            desc = clean(" ".join(words[1:])) or None
                    else:
                        desc = clean(" ".join(words[1:])) or None
                else:
                    name = text
        # cleanup known better names from full text patterns
        for prefix in ("Rolodexer", "Signature Block", "Fast Round", "Alt", "Atlys", "Certn",
                       "Clicky", "Cytronic", "Deel", "Eigen", "Extropic", "Fin"):
            if text.startswith(prefix):
                name = prefix if prefix != "Fin" else "Fin"
                rest = text[len(prefix):].strip()
                if rest.startswith("("):
                    # Fin (fka Intercom)...
                    name = "Fin"
                desc = clean(rest) or desc
                break
        if not name or name.lower() in seen:
            continue
        if name.lower() in ("home", "about", "blog", "team"):
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(href),
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
