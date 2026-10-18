#!/usr/bin/env python3
"""FinTech Collective portfolio scraper -> fintechcollective_companies.json
Source: https://www.fintech.io/portfolio — client-rendered list read from the rendered
DOM via headless Chrome (_chrome_dom.py). Each company row gives name, one-line
action statement, long description, industry, CEO, "Investor Since" stage (the round
FinTech Collective entered at), website and the firm's own "Exited" label."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.fintech.io/portfolio"
PRIMARY = "FinTech Collective"
SECTOR_MAP = {"capital markets": ["FinTech / Insurance"], "banking": ["FinTech / Insurance"],
              "payments": ["FinTech / Insurance"], "insurance": ["FinTech / Insurance"],
              "wealth management": ["FinTech / Insurance"], "lending": ["FinTech / Insurance"],
              "real estate": ["PropTech", "FinTech / Insurance"], "crypto": ["Web3 / Crypto", "FinTech / Insurance"],
              "defi": ["Web3 / Crypto", "FinTech / Insurance"], "digital assets": ["Web3 / Crypto", "FinTech / Insurance"],
              "infrastructure": ["FinTech / Insurance", "Dev Tools / Cloud"], "regtech": ["RegTech/Gov/Legal", "FinTech / Insurance"],
              "data": ["Data & Analytics", "FinTech / Insurance"], "enterprise": ["FinTech / Insurance"],
              "smb": ["FinTech / Insurance"], "asset management": ["FinTech / Insurance"], "proptech": ["PropTech", "FinTech / Insurance"], "consumer": ["Consumer", "FinTech / Insurance"]}


def labelled(p):
    """'Industry:' / 'CEO' / 'Investor Since:' / 'Visit:' label -> following link."""
    out = {}
    for lab in p.select("span.color--blue-mid"):
        key = (clean(lab.get_text(" ", strip=True)) or "").rstrip(":").lower()
        a = lab.find_next("a")
        if key and a:
            out[key] = a
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=150000), "html.parser")
    out, seen = [], set()
    for c in s.select(".portfolio-index__company"):
        tp = c.select_one(".portfolio-index__company__title p")
        if not tp:
            continue
        act = tp.select_one(".portfolio-index__company__action")
        one = clean(act.get_text(" ", strip=True)) if act else None
        if act:
            act.extract()
        name = clean(tp.get_text(" ", strip=True))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        det = c.select_one(".portfolio-index__company__details")
        long = None
        if det:
            ps = [clean(x.get_text(" ", strip=True)) for x in det.select(".col.c9--md p")]
            long = " ".join(x for x in ps if x) or None
        info = labelled(det) if det else {}
        ind = clean(info["industry"].get_text(" ", strip=True)) if "industry" in info else None
        ceo = clean(info["ceo"].get_text(" ", strip=True)) if "ceo" in info else None
        stage = clean(info["investor since"].get_text(" ", strip=True)) if "investor since" in info else None
        w = info.get("visit")
        web = w["href"].strip() if w is not None and w.get("href", "").startswith("http") and not is_social(w["href"]) else None
        exited = c.select_one(".portfolio-detail__exit") is not None
        desc = f"{name} {one}" if one else long
        out.append(rec(name, desc, web, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[ind] if ind else [], sector_map=SECTOR_MAP, industry=ind,
                       long_description=long if one else None, ceo=ceo, stage=stage,
                       status="exited" if exited else "active"))
    if len(out) < 50:
        raise SystemExit(f"FATAL: only {len(out)} FinTech Collective companies")
    finish(out, "fintechcollective", ("description", "company_url", "industry", "ceo", "stage", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
