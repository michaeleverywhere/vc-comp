"""Scrapers for the 2026-10-20 late-night accelerator add (chunk B).
Usage: python batch_oct20b.py [slug...]

Sources: each accelerator's own public portfolio / cohort pages (or the data those pages
load in a browser), plus company websites for blank descriptions. Never Crunchbase /
LinkedIn / PitchBook. Tags are keyword-only (automation/tags.py), no LLM.
"""
from __future__ import annotations

import html as _h
import json
import re
import sys
import threading

import cdp
from batch_oct8 import finish, rec, year_batch
from batch_oct12 import first, get, no_batch, txt
from common import dedupe, enrich_from_sites, save


def enrich_capped(out, limit=420):
    """enrich_from_sites (company websites, blank descriptions only) with an overall time cap
    so one slow company site cannot stall the run."""
    todo = [r for r in out if r.get("website") and not r.get("description")]
    t = threading.Thread(target=enrich_from_sites, args=(todo,), daemon=True)
    t.start()
    t.join(limit)


def _web(u):
    u = (u or "").strip()
    if not u:
        return ""
    return u if u.startswith("http") else "https://" + u


# ---------------- gener8tor (incl. gBETA) ----------------
def gener8tor():
    page = "https://www.gener8tor.com/portfolio"
    res = cdp.capture(page, r"api\.airtable\.com/v0/[^/]+/Alumni", wait=60, port=9521, prof="/tmp/cdp_g8")
    seen, out = set(), []
    for x in res:
        try:
            recs = json.loads(x["body"]).get("records", [])
        except Exception:
            continue
        for r in recs:
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            f = r["fields"]
            name = (f.get("Company Name") or "").strip()
            if not name or str(f.get("On Website", "True")) == "False":
                continue
            prog = (f.get("Web App Program Record") or f.get("Programs") or "").strip()
            desc = (f.get("Description") or "").strip()
            st = (f.get("Operating Status") or "").strip()
            if str(f.get("Exited")) == "1":
                desc = (desc + " (Exited, per gener8tor)").strip()
            elif st and st != "Operating":
                desc = (desc + f" (Status per gener8tor: {st})").strip()
            fund = f.get("Cumulative Funding")
            amt = ""
            try:
                if fund and float(fund) > 0:
                    amt = f"${float(fund):,.0f} cumulative funding (per gener8tor)"
            except Exception:
                pass
            loc = ", ".join(x for x in (f.get("City"), f.get("State")) if x)
            out.append(rec(name, "gener8tor", "gener8tor", description=desc,
                           website=_web(f.get("Vue Website URL") or f.get("Company Website")),
                           team=f.get("Founders") or "", amount_raised=amt,
                           verticals=(f.get("Industries") or "").replace(", ", "; "),
                           date=prog or (f.get("Type") or "gener8tor"), location=loc or "USA",
                           linkedin_url=f.get("LinkedIn") or "", source_url=page,
                           program_type=f.get("Type") or ""))
    out = dedupe(out)
    enrich_capped(out)
    return finish(year_batch(out))


# ---------------- Berkeley SkyDeck ----------------
def skydeck():
    url = "https://skydeck.berkeley.edu/portfolio/"
    s = cdp.render(url, settle=10, port=9522, prof="/tmp/cdp_skydeck")
    out = []
    for web, name, code in re.findall(r'<div class="company-block-item"><div class="name"><a class="company-link" href="([^"]*)">(.*?)</a></div><div class="code">(.*?)</div>', s, re.S):
        out.append(rec(_h.unescape(txt(name)), "Berkeley SkyDeck", "Berkeley SkyDeck", website=web,
                       date=f"SkyDeck {txt(code)}" if txt(code) else "SkyDeck", location="Berkeley, CA, USA",
                       source_url=url))
    out = dedupe(out)
    enrich_capped(out)
    nums = [int(first(r'Batch (\d+)', r["date"]) or 0) for r in out]
    top = max(nums) if nums else 0
    for r, n in zip(out, nums):
        r["batch_date"], r["batch_date_precision"] = "", ""
        r["most_recent_batch"] = bool(top and n == top)
    return finish(out)


# ---------------- Harvard Innovation Labs ----------------
LABS = {"student-i-lab": "Student i-lab", "alumni-launch-lab": "Alumni Launch Lab",
        "pagliuca-harvard-life-lab": "Pagliuca Harvard Life Lab", "life-lab": "Pagliuca Harvard Life Lab"}


def harvardilab():
    base = "https://innovationlabs.harvard.edu/ventures"
    out = []
    for pg in range(1, 40):
        s = get(base if pg == 1 else f"{base}/p{pg}")
        cards = re.findall(r'<a href="(https://innovationlabs\.harvard\.edu/venture/[^"]+)" class="venture-card ([^"]*)"(.*?)</a>', s, re.S)
        if not cards:
            break
        for href, cls, body in cards:
            name = txt(first(r'class="venture-card__title">(.*?)</h3>', body))
            if not name:
                continue
            desc = txt(first(r'class="venture-card__description">(.*?)</p>', body))
            labs = [v for k, v in LABS.items() if k in cls.split()]
            out.append(rec(name, "Harvard Innovation Labs", "Harvard Innovation Labs", description=desc,
                           date="Harvard Innovation Labs " + (labs[0] if labs else "venture"),
                           location="Boston (Allston), MA, USA", source_url=href))
        if f"/ventures/p{pg + 1}" not in s:
            break
    out = dedupe(out)
    return finish(no_batch(out))


# ---------------- Founder Institute ----------------
def founderinstitute():
    url = "https://fi.co/graduates"
    s = get(url)
    out = []
    for blk in s.split("js-graduate-each")[1:]:
        name = txt(first(r'<h3[^>]*>(.*?)</h3>', blk))
        if not name:
            continue
        loc = txt(first(r'<span class=[\'"]md:mt-1[^\'"]*[\'"]>(.*?)</span>', blk))
        desc = txt(first(r'<p class=[\'"]md:mt-2[^\'"]*[\'"]>(.*?)</p>', blk))
        web = first(r'target=[\'"]_blank[\'"] rel=[\'"]nofollow[\'"] href=[\'"](https?://[^\'"]+)[\'"]', blk)
        team = txt(first(r'Founder\(s\)</span>\s*<p[^>]*>(.*?)</p>', blk))
        tail = re.sub(r'<[^>]+>', ' ', blk.split("Founder(s)")[-1])[:300]
        acq = bool(re.search(r'\bAcquired\b', tail))
        out.append(rec(name, "Founder Institute", "Founder Institute",
                       description=desc + (" (Acquired, per Founder Institute)" if acq else ""),
                       website=web, team=team, date="Founder Institute graduate (featured portfolio)",
                       location=loc, source_url=url))
    out = dedupe(out)
    return finish(no_batch(out))


# ---------------- MIT delta v ----------------
def mitdeltav():
    url = "https://entrepreneurship.mit.edu/accelerator/past-teams/"
    s = get(url)
    body = s.split("<body", 1)[-1]
    out, year = [], ""
    tok = re.compile(r'<h[1-6][^>]*>\s*(?:<[^>]+>\s*)*(20\d\d|19\d\d)\s*(?:<[^>]+>\s*)*</h[1-6]>|<li>(.*?)</li>', re.S)
    for m in tok.finditer(body):
        if m.group(1):
            year = m.group(1)
            continue
        if not year:
            continue
        inner = m.group(2)
        href = first(r'<a href="([^"]*)"', inner)
        a_text = txt(first(r'<a [^>]*>(.*?)</a>', inner))
        rest = txt(re.sub(r'<a [^>]*>.*?</a>', ' ', inner, flags=re.S))
        name = a_text or txt(re.split(r'<br|\(', inner)[0])
        note = rest if a_text else txt(inner[len(re.split(r'<br|\(', inner)[0]):])
        if not name or len(name) > 80 or re.search(r"demo day|watch|apply|menu|login|privacy|contact", name, re.I):
            continue
        if "mit.edu" in href:
            continue
        out.append(rec(name, "MIT delta v", "MIT delta v", website=href if href.startswith("http") else "",
                       description=note if note.startswith("(") else "", date=f"MIT delta v {year}",
                       location="Cambridge, MA, USA", source_url=url))
    # current cohort page (not yet on Past Teams)
    cur = "https://entrepreneurship.mit.edu/accelerator/2026-delta-v/"
    try:
        s2 = get(cur)
    except Exception:
        s2 = ""
    for name, tagline, rest in re.findall(r'<div class="fusion-text[^"]*"><h1>(.*?)</h1>\s*<h3>(.*?)</h3>(.*?)</div>', s2, re.S):
        desc = txt(first(r'<p[^>]*>(.*?)</p>', rest))
        web = first(r'<a href="(https?://[^"]+)"', rest)
        out.append(rec(txt(name), "MIT delta v", "MIT delta v", description=(txt(tagline) + ". " + desc).strip(". "),
                       website=web, date="MIT delta v 2026", location="Cambridge, MA, USA", source_url=cur))
    out = dedupe(out)
    enrich_capped(out)
    return finish(year_batch(out))


# ---------------- Melbourne Accelerator Program (MAP) ----------------
def melbourneaccelerator():
    url = "https://www.themap.co/startups"
    s = get(url)
    out, year = [], ""
    tok = re.compile(r'class="list-section-title"[^>]*>\s*<p[^>]*>\s*(20\d\d)\s*</p>|data-current-context="([^"]+)"', re.S)
    for m in tok.finditer(s):
        if m.group(1):
            year = m.group(1)
            continue
        try:
            d = json.loads(_h.unescape(m.group(2)))
        except Exception:
            continue
        for it in d.get("userItems") or []:
            name = txt(_h.unescape(it.get("title") or ""))
            if not name:
                continue
            paras = [txt(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', _h.unescape(it.get("description") or ""), re.S)]
            paras = [p for p in paras if p] or [txt(_h.unescape(it.get("description") or ""))]
            team = ""
            if paras and re.match(r'Founders?\s*:', paras[0]):
                team = re.sub(r'^Founders?\s*:\s*', '', paras.pop(0))
            desc = " ".join(paras)
            web = ((it.get("button") or {}).get("buttonLink") or "")
            out.append(rec(name, "Melbourne Accelerator Program (MAP)", "MAP", description=desc, team=team,
                           website=web if web.startswith("http") else "",
                           date=f"MAP {year} cohort" if year else "MAP", location="Melbourne, Australia",
                           source_url=url))
    out = dedupe(out)
    enrich_capped(out)
    return finish(year_batch(out))


FUNCS = {
    "gener8tor": gener8tor,
    "skydeck": skydeck,
    "harvardilab": harvardilab,
    "founderinstitute": founderinstitute,
    "mitdeltav": mitdeltav,
    "melbourneacceleratorprogram": melbourneaccelerator,
}

if __name__ == "__main__":
    for slug in sys.argv[1:] or list(FUNCS):
        print(f"=== {slug} ===", flush=True)
        recs = FUNCS[slug]()
        save(slug, recs, {"source_fn": f"batch_oct20b.{FUNCS[slug].__name__}"})
