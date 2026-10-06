#!/usr/bin/env python3
"""Lightspeed Venture Partners portfolio scraper (lsvp.com/companies).

Writes data/companies.json (historic filename for Lightspeed). Includes every
company on the lsvp.com/companies listing; `lsvp_investor_flag` keeps the site's
data-investor value (lsvp | both | lsip, where lsip = Lightspeed India Partners,
whose detail pages live on lsip.com). Fields come only from the firm's own pages.
"""
import json, re, sys, html, time, os
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup

LIST_URL = "https://lsvp.com/companies/"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "companies.json")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
S = requests.Session(); S.headers.update(UA)

def get(url, tries=3):
    for i in range(tries):
        try:
            r = S.get(url, timeout=30)
            if r.status_code == 200:
                return r.text
        except requests.RequestException:
            pass
        time.sleep(1.5 * (i + 1))
    return None

def clean(t):
    return re.sub(r"\s+", " ", html.unescape(t or "")).strip() or None

def to_int(v):
    m = re.search(r"\b(19|20)\d{2}\b", v or "")
    return int(m.group(0)) if m else None

def parse_listing(h):
    soup = BeautifulSoup(h, "html.parser")
    out = []
    for li in soup.select("li[data-company-id][data-investor]"):
        inv = li.get("data-investor")
        if inv not in ("lsvp", "both", "lsip"):
            continue
        a = li.find("a", href=True)
        if not a or not re.search(r"(lsvp|lsip)\.com/company/", a["href"]):
            continue
        name = clean(li.find("h5").find(string=True, recursive=False) if li.find("h5") else None)
        info = {}
        for item in li.select("ul.company-info-list li"):
            k = clean(item.find("strong").get_text(" ")) if item.find("strong") else None
            v = clean(item.find("span").get_text(" ")) if item.find("span") else None
            if k: info[k.lower()] = v
        out.append(dict(slug=li["data-company-id"], investor=inv, url=a["href"], name=name, info=info))
    return out

def parse_detail(h):
    soup = BeautifulSoup(h, "html.parser")
    d = {}
    t = soup.select_one(".founder-title")
    d["name"] = clean(t.get_text()) if t else None
    for dl in soup.select(".info-box dl"):
        k = clean(dl.find("dt").get_text()) if dl.find("dt") else None
        v = clean(dl.find("dd").get_text(" ")) if dl.find("dd") else None
        if k: d[k.lower()] = v
    lead, team = [], []
    for blk in soup.select(".info-box-wrap--lsip .df"):
        head = blk.select_one(".df-t")
        if not head: continue
        items = [clean(x.get_text(" ")) for x in blk.find_all("div", recursive=False) if x is not head]
        items = [x for x in items if x]
        h_ = clean(head.get_text()).lower()
        if "leadership" in h_: lead = items
        elif "lightspeed team" in h_: team = items
    d["leadership"], d["team"] = lead, team
    a = soup.select_one("a#company_url[href]")
    d["company_url"] = a["href"].strip() if a and a["href"].startswith("http") else None
    img = soup.select_one(".banner-logo img[src]")
    d["logo_url"] = img["src"] if img else None
    desc = soup.select_one(".desc")
    d["description"] = clean(desc.get_text(" ")) if desc else None
    d["social_urls"] = [x["href"] for x in soup.select("ul.links a[href]") if x["href"].startswith("http")]
    return d

def build(item, det, ts):
    info = item["info"]; det = det or {}
    status_full = det.get("status") or info.get("status")
    exit_type = acquirer = ticker = None; exit_desc = None
    if status_full:
        m = re.match(r"(Acquired|Merged|IPO|Public)\s*(.*)", status_full, re.I)
        if m:
            exit_type = m.group(1).title() if m.group(1).lower() != "ipo" else "IPO"
            exit_desc = clean(m.group(2))
            am = re.match(r"by\s+(.+)", exit_desc or "", re.I)
            if am: acquirer = clean(am.group(1))
            tm = re.search(r"\(?([A-Z]{2,6}):\s*([A-Z.]{1,6})\)?", status_full)
            if tm: ticker = tm.group(2)
    stage = det.get("stage invested") or info.get("stage invested")
    year = to_int(det.get("lsvp investment") or info.get("backed since"))
    founders = [re.split(r"\s+-\s+", x)[0] for x in det.get("leadership", [])]
    return {
        "company_name": det.get("name") or item["name"],
        "description": det.get("description"),
        "current_stage": None,
        "partners": [re.split(r"\s+-\s+", x)[0] for x in det.get("team", [])],
        "leadership": det.get("leadership", []),
        "founders": [],
        "sectors": [],
        "year_founded": to_int(det.get("founded") or info.get("founded")),
        "first_partnered_stage": stage,
        "first_partnered_year": year,
        "first_partnered_date": str(year) if year else None,
        "initial_investment_type": stage,
        "site_status": status_full,
        "exit_type": exit_type,
        "exit_description": exit_desc,
        "ticker_symbol": ticker,
        "acquirer": acquirer,
        "lsvp_investor_flag": item["investor"],
        "company_profile_url": item["url"],
        "company_url": det.get("company_url"),
        "social_urls": det.get("social_urls", []),
        "logo_url": det.get("logo_url"),
        "image_url": None,
        "source_url": LIST_URL,
        "scraped_at": ts,
    }

def main():
    limit = None
    if "--limit" in sys.argv: limit = int(sys.argv[sys.argv.index("--limit") + 1])
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    h = get(LIST_URL)
    if not h: sys.exit("listing fetch failed")
    items = parse_listing(h)[:limit]
    print(f"listing: {len(items)} companies")
    with ThreadPoolExecutor(8) as ex:
        pages = list(ex.map(lambda it: get(it["url"]), items))
    recs = []
    miss = 0
    for it, p in zip(items, pages):
        det = parse_detail(p) if p else None
        if not p: miss += 1
        recs.append(build(it, det, ts))
    json.dump(recs, open(OUT, "w"), indent=2, ensure_ascii=False)
    print(f"wrote {len(recs)} companies -> {OUT} (detail fetch failures: {miss})")
    for f in ("description", "company_url", "year_founded", "first_partnered_stage", "first_partnered_year", "partners", "site_status"):
        print(f"  {f:22s} filled {sum(1 for r in recs if r.get(f))}/{len(recs)}")

if __name__ == "__main__":
    main()
