#!/usr/bin/env python3
"""Jump Capital portfolio scraper -> jumpcapital_companies.json
Source: https://jumpcap.com/portfolio/ — the page lists every company as a
`.portfolio-modal-content` stub (data-status active/exited, data-verticals);
the modal body (description, founders, related press) comes from the site's
own public `fetch_modal_content` admin-ajax call, the same request the page's
JS makes. Websites are not published.
"""
import os, re, sys, json, time
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, prune_substring_tags, apply_tag_overrides, carry_forward_descriptions, HEADERS
from _d20_common import write_out

SOURCE_URL = "https://jumpcap.com/portfolio/"
AJAX = "https://jumpcap.com/wp-admin/admin-ajax.php"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "jumpcapital_companies.json")
PRIMARY = "Jump Capital"
VERTICALS = {"application-software": "Application Software", "fintech": "Fintech",
             "cybersecurity": "Cybersecurity", "infrastructure-software": "Infrastructure Software"}
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "cybersecurity": ["Cybersecurity"],
              "infrastructure software": ["Dev Tools / Cloud"]}
TAG_OVERRIDES = {
    "Prompt Security": ["Cybersecurity"],
    "Blitzy": ["Dev Tools / Cloud"],
    "Siemplify": ["Cybersecurity"],
    "Acres": ["PropTech", "Data & Analytics"],
    "Bitgo": ["Web3 / Crypto", "FinTech / Insurance"],
    "Booker": ["Consumer"],
    "Champion": ["RegTech/Gov/Legal", "Data & Analytics"],
    "CoinDCX": ["Web3 / Crypto", "FinTech / Insurance"],
    "Consensys": ["Web3 / Crypto"],
    "Curv": ["Web3 / Crypto", "Cybersecurity"],
    "Digital Assets Data": ["Web3 / Crypto", "Data & Analytics"],
    "Gauss": ["Health"],
    "HealthExpense": ["Health", "FinTech / Insurance"],
    "HubTran": ["Logistics / Supply Chain", "FinTech / Insurance"],
    "IRONSCALES": ["Cybersecurity"],
    "Kinetiq": ["Data & Analytics", "Gaming / Media / Entertainment"],
    "LinkSquares": ["RegTech/Gov/Legal"],
    "LISNR": ["Dev Tools / Cloud", "FinTech / Insurance"],
    "LogicGate": ["RegTech/Gov/Legal", "Cybersecurity"],
    "M1": ["FinTech / Insurance", "Consumer"],
    "Made Card": ["FinTech / Insurance", "PropTech"],
    "Mobly": ["Future of Work"],
    "NowSecure": ["Cybersecurity"],
    "Pluto Security": ["Cybersecurity"],
    "Pyth": ["Web3 / Crypto", "FinTech / Insurance"],
    "Reputation": ["Data & Analytics"],
    "Shipa": ["Dev Tools / Cloud"],
    "Snoots": ["Health", "Consumer"],
    "Spire": ["Data & Analytics", "Deeptech / Robotics / AR/VR"],
    "Spring": ["FinTech / Insurance", "Data & Analytics"],
    "Swiftpage": ["Future of Work"],
    "Teikametrics": ["Consumer", "Data & Analytics"],
    "The Savings Group": ["FinTech / Insurance", "Consumer"],
    "Toolio": ["Consumer", "Data & Analytics"],
    "Tradingview": ["FinTech / Insurance", "Consumer"],
    "TRM": ["Web3 / Crypto", "Cybersecurity"],
    "True Fit": ["Consumer", "Data & Analytics"],
    "UPshow": ["Gaming / Media / Entertainment"],
    "Visibly": ["Health"],
    "Zerox": ["Web3 / Crypto", "Dev Tools / Cloud"],
    "Certora": ["Web3 / Crypto", "Cybersecurity"],
    "Notabene": ["Web3 / Crypto", "RegTech/Gov/Legal"],
}
ROLE_RX = re.compile(r"(?i)founder|ceo|cto|coo|president|chief")


def modal_batch(stubs):
    data = {"action": "fetch_modal_content"}
    for i, (pid, sid) in enumerate(stubs):
        data[f"check_list[{i}][index]"] = str(i)
        data[f"check_list[{i}][pageId]"] = str(pid)
        data[f"check_list[{i}][hasLoading]"] = "true"
        data[f"check_list[{i}][target]"] = f"#m #{sid}"
    for attempt in range(3):
        try:
            r = requests.post(AJAX, data=data, headers=HEADERS, timeout=30)
            r.raise_for_status()
            return {str(x.get("pageId")): x.get("content") or "" for x in r.json()}
        except (requests.RequestException, ValueError):
            time.sleep(2 * (attempt + 1))
    return {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    stubs, seen_ids = [], set()
    for m in soup.select(".portfolio-modal-content"):
        pid = m.get("data-post-id")
        if not pid or pid in seen_ids:
            continue
        seen_ids.add(pid)
        img = m.select_one("img[alt]")
        name = clean(re.sub(r"(?i)\s*logo$", "", img["alt"])) if img else None
        if not name:
            name = clean((m.get("id") or "").replace("portfolio-", "").replace("-", " ").title())
        stubs.append({"pid": pid, "sid": m.get("id"), "name": name,
                      "status": (m.get("data-status") or "").lower(),
                      "verticals": [VERTICALS.get(v, v) for v in (m.get("data-verticals") or "").split() if v]})
    contents = {}
    for i in range(0, len(stubs), 7):
        contents.update(modal_batch([(s["pid"], s["sid"]) for s in stubs[i:i + 7]]))
        time.sleep(0.3)
    out, seen = [], set()
    for s in stubs:
        if not s["name"] or s["name"].lower() in seen:
            continue
        seen.add(s["name"].lower())
        d = BeautifulSoup(contents.get(s["pid"], ""), "html.parser")
        h4 = d.select_one(".left-bottom h4") or d.select_one(".info-left-side h4")
        desc = clean(h4.get_text(" ", strip=True)) if h4 else None
        founders = []
        for g in d.select(".info-right-side .group"):
            t = g.select_one(".group-title")
            role = clean(t.get_text(" ", strip=True)) if t else ""
            if role and ROLE_RX.search(role) and "jump" not in role.lower():
                for n in g.select(".polaroid-name"):
                    nm = clean(n.get_text(" ", strip=True))
                    if nm:
                        founders.append({"name": nm, "title": role})
        out.append({
            "company_name": s["name"],
            "description": desc,
            "company_url": None,
            "founders": founders,
            "sectors": s["verticals"],
            "site_status": s["status"] or None,
            "status": "active" if s["status"] == "active" else None,
            "exited": s["status"] == "exited",
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    carry_forward_descriptions(out, OUT)
    for r in out:
        mapped = []
        for v in r["sectors"]:
            for t in SECTOR_MAP.get(v.lower(), []):
                if t not in mapped:
                    mapped.append(t)
        kw = [t for t in tags_for(r["company_name"], r["description"]) if t not in mapped]
        r["everywhere_tags"] = (mapped + kw)[:3]
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "founders", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
