#!/usr/bin/env python3
"""Real Ventures portfolio scraper -> realventures_companies.json
Source: https://realventures.com/portfolio/ — WordPress, one server-rendered
company grid. Each grid item carries the name, a one-line description and
filter classes (Real partner slug, sector slugs, status active/acquired/
exited); acquired items also show "Acquired by <buyer>". Each item's modal
(data-modal="modal-<id><wp post id>") adds a longer description, the CEO and a "More
info" website link. Status: acquired/exited -> "acquired" (raw kept in
site_status), active -> "active".
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, label_after, apply_tag_overrides

SOURCE_URL = "https://realventures.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "realventures_companies.json")
PRIMARY = "Real Ventures"
SECTOR_NAMES = {"ai-robotics": "AI & Robotics", "enterprise": "Enterprise", "health-wellness": "Health & Wellness",
                "consumer": "Consumer", "financial": "Financial", "education": "Education",
                "security-infrastructure": "Security & Infrastructure", "marketplace": "Marketplace",
                "climate": "Climate", "web3": "Web3"}
SECTOR_TAG_MAP = {"health & wellness": ["Health"], "financial": ["FinTech / Insurance"],
                  "security & infrastructure": ["Cybersecurity", "Dev Tools / Cloud"],
                  "ai & robotics": ["Deeptech / Robotics / AR/VR"], "climate": ["Climate / Sustainability"],
                  "transportation": ["Transportation / Mobility"]}


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "PermissionClick": ["Dev Tools / Cloud", "Consumer"],
    "Tenstorrent": ["Deeptech / Robotics / AR/VR"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    modals = {re.sub(r"\d+$", "", m.get("data-modal") or ""): m for m in soup.select(".modal[data-modal]")}
    out, seen = [], set()
    for it in soup.select(".company-grid__grid-item"):
        t = it.select_one(".company-grid__grid-item-title")
        name = clean(t.get_text(" ")) if t else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        ps = [p for p in it.find_all("p") if "company-grid__grid-item-status" not in (p.get("class") or [])]
        short = clean(ps[0].get_text(" ")) if ps else None
        stx = it.select_one(".company-grid__grid-item-status")
        stx = clean(stx.get_text(" ")) if stx else None
        raw_status = clean(it.get("data-company-grid-filter-three"))
        acq = re.match(r"(?i)acquired by\s+(.+)", stx or "")
        sectors = [SECTOR_NAMES.get(x, x.replace("-", " ").title()) for x in (it.get("data-company-grid-filter-two") or "").split()]
        partners = [x.replace("-", " ").title() for x in (it.get("data-company-grid-filter-one") or "").split()]
        m = modals.get("modal-" + (it.get("data-modal-id") or ""))
        long_desc, ceo, url = None, None, None
        if m:
            dd = m.select_one(".modal__description")
            long_desc = clean(dd.get_text(" ")) if dd else None
            det = m.select_one(".modal__details")
            if det:
                ceo = label_after(list(det.stripped_strings), "CEO", "CEOs", "Founder", "Founders", "Co-founders")
                for a in det.select("a[href]"):
                    if a["href"].startswith("http"):
                        url = a["href"].strip()
                        break
        if not url:
            a = t.select_one("a[href^=http]") if t else None
            if a and not acq and "techcrunch" not in a["href"] and "realventures" not in a["href"]:
                url = a["href"].strip()
        status = "acquired" if raw_status in ("acquired", "exited") else ("active" if raw_status == "active" else None)
        desc = short or long_desc
        out.append({
            "company_name": name,
            "description": desc,
            "long_description": long_desc if long_desc and long_desc != desc else None,
            "company_url": url,
            "status": status,
            "site_status": stx or (raw_status.title() if raw_status else None),
            "acquirer": clean(acq.group(1)) if acq else None,
            "ceo": ceo,
            "sectors": sectors,
            "real_partners": partners,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "long_description", "company_url", "status", "acquirer", "ceo", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
