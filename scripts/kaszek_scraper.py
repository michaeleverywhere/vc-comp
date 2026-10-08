#!/usr/bin/env python3
"""Kaszek portfolio scraper -> kaszek_companies.json
Source: https://www.kaszek.com/companies/ — WordPress; the grid is loaded
client-side, so the company list comes from the public WP REST API
(`company` post type) and each /company/<slug>/ page is parsed for the
description paragraphs, founders, website(s), the "<name> is headquartered
in <city>" line (-> location), Investment status (Kaszek's holding status,
e.g. active / exited), Year founded and Company status (e.g. private /
public / acquired).
Status: Company status "acquired" -> acquired; else Investment status
"active" -> active, "exit" -> acquired (repo convention for exited); raw values kept in investment_status / company_status.
"""
import html, json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, label_after, clean_url, is_social, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.kaszek.com/companies/"
API = "https://www.kaszek.com/wp-json/wp/v2/company"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "kaszek_companies.json")
PRIMARY = "Kaszek"

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "ARQ": ["FinTech / Insurance", "Consumer"],
    "Arvo": ["Health", "FinTech / Insurance", "Data & Analytics"],
    "Ayenda": ["Consumer"],
    "Azos": ["FinTech / Insurance"],
    "Bitso": ["Web3 / Crypto", "FinTech / Insurance", "Consumer"],
    "Casai": ["Consumer", "PropTech"],
    "Compara": ["FinTech / Insurance", "Consumer"],
    "Creditas": ["FinTech / Insurance"],
    "Enter": ["RegTech/Gov/Legal", "Future of Work"],
    "Fintual": ["FinTech / Insurance"],
    "Grão Direto": ["Logistics / Supply Chain", "FinTech / Insurance"],
    "Justos": ["FinTech / Insurance"],
    "Kavak": ["Transportation / Mobility", "Consumer", "FinTech / Insurance"],
    "Kushki": ["FinTech / Insurance"],
    "Lemon Energy": ["Climate / Sustainability", "Consumer"],
    "LivUp": ["Consumer", "CPG"],
    "Minka": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "Musa": ["Climate / Sustainability", "Logistics / Supply Chain"],
    "Pitzi": ["FinTech / Insurance", "Consumer"],
    "Primero AI": ["Future of Work"],
    "Remessa": ["FinTech / Insurance"],
    "Segura": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "Sofia": ["Health", "FinTech / Insurance"],
    "Somos": ["Dev Tools / Cloud", "Deeptech / Robotics / AR/VR"],
    "Sou Smile": ["Health", "Consumer"],
    "Tapi": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "Volanty": ["Transportation / Mobility", "Consumer"],
    "Yuno": ["FinTech / Insurance", "Data & Analytics"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    posts, page = [], 1
    while True:
        d = fetch(f"{API}?per_page=100&page={page}&_fields=id,slug,link,title", as_json=True)
        posts += d
        if len(d) < 100:
            break
        page += 1
    posts.sort(key=lambda p: html.unescape(p["title"]["rendered"]).lower())
    if limit:
        posts = posts[:limit]
    details = fetch_many([p["link"] for p in posts], workers=4, pause=0.4)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for p in posts:
        name = clean(html.unescape(p["title"]["rendered"]))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = site = loc = inv = comp = founded = None
        founders = []
        h = details.get(p["link"])
        if h:
            s = BeautifulSoup(h, "html.parser")
            for t in s(["script", "style", "svg", "nav", "footer", "header", "noscript"]):
                t.decompose()
            st = [clean(x) for x in s.body.stripped_strings if clean(x)]
            stop = st.index("Founders") if "Founders" in st else len(st)
            paras = [x for x in st[:stop] if len(x) > 50]
            desc = " ".join(paras[:2]) or None
            if "Founders" in st:
                i = st.index("Founders") + 1
                while i < len(st) and not st[i].lower().startswith(("website", "linkedin", "facebook", "twitter", "instagram", "youtube")) \
                        and st[i] not in ("Investment status", "Year founded", "Company status") \
                        and len(st[i]) < 60 and not st[i].startswith(name + " "):
                    founders.append(re.sub(r",.*$", "", st[i]).strip(" ;"))
                    i += 1
            for x in st:
                m = re.search(r"is headquartered in ([^.]+?)(?: and | but |, where|\.|$)", x)
                if m:
                    loc = clean(m.group(1))
                    break
            inv = label_after(st, "Investment status")
            comp = label_after(st, "Company status")
            fy = label_after(st, "Year founded")
            founded = int(fy) if fy and re.fullmatch(r"\d{4}", fy) else None
            for a in s.select("a[href^=http]"):
                if "kaszek.com" in a["href"] or is_social(a["href"]):
                    continue
                if clean(a.get_text(" ")) and "website" in clean(a.get_text(" ")).lower() or not site:
                    site = site or a["href"]
        if (comp or "").lower() == "acquired":
            status = "acquired"
        elif (inv or "").lower() == "active":
            status = "active"
        elif (inv or "").lower() in ("exit", "exited"):
            status = "acquired"
        else:
            status = None
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(site),
            "company_profile_url": p["link"],
            "status": status,
            "investment_status": inv,
            "company_status": comp,
            "location": loc,
            "year_founded": founded,
            "founders": founders,
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, None)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "location", "year_founded", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
