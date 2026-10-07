# Mosaic Ventures portfolio scraper (rewritten 2026-10-07).
# Source: https://mosaicventures.com/portfolio (Squarespace user-items lists).
# Each card: <a><strong>Name</strong></a> (company site) / tagline / "Founded, YYYY" /
# "Partnered, YYYY" / optional "Acquired by X, YYYY" or "IPO, YYYY" / "<u>sectors..., Status</u>".
# Cards under "Companies we backed prior to Mosaic" are partners' pre-Mosaic deals and are skipped.
import re
import requests
import bs4

SOURCE = "https://mosaicventures.com/portfolio"
STATUS_WORDS = {"active": "active", "exited": "exited", "acquired": "acquired", "ipo": "IPO", "public": "IPO"}


def _parse_card(desc):
    ps = desc.find_all("p")
    if not ps:
        return None
    a = ps[0].find("a")
    name = ps[0].get_text(" ", strip=True)
    if not name:
        return None
    rec = {
        "company_name": name,
        "company_url": a.get("href").strip() if a and a.get("href", "").startswith("http") else None,
        "description": None,
        "year_founded": None,
        "year_partnered": None,
        "sectors": [],
        "status": None,
        "acquirer": None,
        "exit_year": None,
        "exit_note": None,
        "source_url": SOURCE,
    }
    lines = []
    for p in ps[1:]:
        for br in p.find_all("br"):
            br.replace_with("\n")
        lines += [l.strip() for l in p.get_text().split("\n") if l.strip()]
    tagline = []
    for l in lines:
        m = re.match(r"^Founded,?\s*(\d{4})", l)
        if m:
            rec["year_founded"] = m.group(1); continue
        m = re.match(r"^Partnered,?\s*(\d{4})", l)
        if m:
            rec["year_partnered"] = m.group(1); continue
        m = re.match(r"^(Acquired by .+?|IPO|Merged with .+?|Listed .+?)(?:,\s*(\d{4}))?$", l)
        if m and (l.lower().startswith(("acquired by", "ipo", "merged with", "listed"))):
            rec["exit_note"] = l
            rec["exit_year"] = m.group(2)
            if l.lower().startswith("acquired by"):
                rec["acquirer"] = re.sub(r"^Acquired by\s+", "", m.group(1)).strip()
            continue
        parts = [x.strip() for x in l.split(",") if x.strip()]
        if parts and parts[-1].lower() in STATUS_WORDS and all(len(x) < 40 for x in parts):
            st = parts[-1].lower()
            rec["status"] = STATUS_WORDS[st]
            rec["sectors"] = [x for x in parts if x.lower() not in STATUS_WORDS]
            continue
        tagline.append(l)
    rec["description"] = " ".join(tagline) or None
    if rec["acquirer"]:
        rec["status"] = "acquired"
    elif rec["exit_note"] and rec["exit_note"].lower().startswith("ipo"):
        rec["status"] = "IPO"
    return rec


def scrape() -> list[dict]:
    r = requests.get(SOURCE, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=30)
    r.raise_for_status()
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    out, seen = [], set()
    prior = False
    for el in soup.find_all(True):
        if el.name in ("h1", "h2", "h3", "h4", "p") and "prior to mosaic" in el.get_text(" ", strip=True).lower() and len(el.get_text()) < 120:
            prior = True
        if prior:
            continue
        if el.name == "div" and "list-item-content__description" in (el.get("class") or []):
            rec = _parse_card(el)
            if rec and rec["company_name"].lower() not in seen and (rec["year_partnered"] or rec["status"]):
                seen.add(rec["company_name"].lower())
                out.append(rec)
    return out


# --- auto-appended runner (trusted template, not LLM output) -----------------
if __name__ == "__main__":
    import json as _json, os as _os, sys as _sys
    from datetime import datetime as _dt, timezone as _tz
    _records = scrape()
    _now = _dt.now(_tz.utc).replace(microsecond=0).isoformat()
    for _r in _records:
        _r.setdefault("everywhere_tags", [])
        _r.setdefault("scraped_at", _now)
    _out = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                         "..", "data", "mosaicventures_companies.json")
    with open(_out, "w") as _f:
        _json.dump(_records, _f, indent=2, ensure_ascii=False)
        _f.write("\n")
    print(f"wrote {len(_records)} records")
