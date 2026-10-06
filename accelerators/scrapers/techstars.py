"""Techstars: every company in techstars.com/portfolio (all programs, all years).

Source: the public Typesense search behind techstars.com/portfolio; its search-only
config (url, collection, key) is served by techstars.com/api/search/config/companies.
Fields used: company_name, brief_description, industry_vertical (Techstars' own
labels -> Verticles), program_names + first_session_year (-> Date of Announcement),
website. Techstars does not publish founders, round, or amount in the directory.
crunchbase_url is dropped; linkedin_url is kept only as the URL Techstars itself lists (LinkedIn is never fetched).
"""
import requests

from common import UA, clean, dedupe, save, tag

CFG = "https://www.techstars.com/api/search/config/companies"


def main():
    cfg = requests.get(CFG, headers=UA, timeout=30).json()
    url = f"{cfg['url']}/collections/{cfg['collection']}/documents/search"
    h = {"X-TYPESENSE-API-KEY": cfg["apiKey"]}
    docs, page = [], 1
    while True:
        r = requests.get(url, headers=h, params={"q": "*", "per_page": 250, "page": page}, timeout=60)
        r.raise_for_status()
        d = r.json()
        docs += [x["document"] for x in d["hits"]]
        if not d["hits"] or len(docs) >= d["found"]:
            break
        page += 1
    print(f"[techstars] fetched {len(docs)} of {d['found']}")
    recs = []
    for x in docs:
        progs = [clean(p) for p in (x.get("program_names") or []) if p]
        yr = x.get("first_session_year")
        short = [p.replace(" Accelerator", "") for p in progs]
        date = "; ".join(short) if short else "Techstars"
        if yr:
            date = f"{date} {yr}"
        labels = x.get("industry_vertical") or []
        site = clean(x.get("website"))
        recs.append({
            "name": clean(x["company_name"]),
            "description": clean(x.get("brief_description")),
            "website": ("https://" + site) if site and not site.startswith("http") else site,
            "team": "", "round": "", "amount_raised": "",
            "date": date,
            "verticals": "; ".join(labels),
            "linkedin_url": x.get("linkedin_url") or "",
            "investors": "Techstars",
            "source": "Techstars",
            "everywhere_tags": tag(x["company_name"], x.get("brief_description"), labels),
            "programs": progs,
            "first_session_year": yr,
            "is_accelerator_company": x.get("is_accelerator_company"),
            "is_exit": x.get("is_exit"),
            "location": ", ".join(v for v in [x.get("city"), x.get("state_province"), x.get("country")] if v),
            "source_url": "https://www.techstars.com/portfolio",
        })
    recs = dedupe(recs)
    save("techstars", recs, {"source": "https://www.techstars.com/portfolio",
                             "method": "public Typesense index (search-only key from /api/search/config)"})


if __name__ == "__main__":
    main()
