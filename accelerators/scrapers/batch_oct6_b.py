"""Scrapers for 2026-10-06 batch B (next 10 queued). Usage:
  python batch_oct6_b.py [slug...]
"""
from __future__ import annotations

import html as _h
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote

import requests

from common import UA, clean, dedupe, enrich_from_sites, save, tag

SESSION = requests.Session()
SESSION.headers.update(UA)


def get(url, **kw):
    r = SESSION.get(url, timeout=kw.pop("timeout", 60), **kw)
    r.raise_for_status()
    return r.text


def strip(s):
    return clean(_h.unescape(re.sub(r"<[^>]+>", " ", s or "")))


def rec(name, acc, source, **kw):
    r = {
        "name": clean(name),
        "description": "",
        "website": "",
        "team": "",
        "round": "",
        "amount_raised": "",
        "date": "",
        "verticals": "",
        "investors": acc,
        "source": source,
        "everywhere_tags": [],
        "source_url": "",
    }
    r.update({k: (clean(v) if isinstance(v, str) else v) for k, v in kw.items()})
    if not r["everywhere_tags"]:
        r["everywhere_tags"] = tag(
            r["name"], r["description"], [x for x in r["verticals"].split("; ") if x]
        )
    return r


# ---- LAUNCH (homepage logo wall) ----
LAUNCH_SKIP = {"LAUNCH", "Launch", "Jason Calacanis, LAUNCH Founder"}


def launch():
    url = "https://launch.co/"
    s = get(url)
    # Portfolio logo wall: img alts of company names (duplicated in mobile/desktop)
    alts = re.findall(r'<img[^>]+alt="([^"]+)"', s)
    names = []
    for a in alts:
        a = clean(a)
        if not a or a in LAUNCH_SKIP or a in names:
            continue
        # skip obvious non-companies
        if "calacanis" in a.lower() or a.upper() == "LAUNCH":
            continue
        names.append(a)
    # Only keep names that appear near portfolio section if possible
    out = []
    for n in names:
        out.append(
            rec(
                n,
                "LAUNCH Accelerator",
                "LAUNCH",
                date="LAUNCH",
                source_url=url,
                everywhere_tags=tag(n, ""),
            )
        )
    enrich_from_sites(out)  # websites unknown from logo wall
    return out


# ---- Gravity Labs ----
def gravitylabs():
    url = "https://gravity-labs.xyz/portfolio.html"
    s = get(url)
    out = []
    stealth_i = 0
    for block in re.split(r"<h4>", s)[1:]:
        raw_name = strip(block.split("</h4>")[0])
        desc = strip((re.search(r"<p>(.*?)</p>", block, re.S) or [None, ""])[1])
        href = re.search(r'href="(https?://[^"]+)"', block)
        name = raw_name
        if re.fullmatch(r"Stealth(?:\s*\(.*\))?", name, re.I) or name == "Stealth":
            stealth_i += 1
            # keep distinct rows using published one-liner
            short = desc.split(".")[0][:60] if desc else str(stealth_i)
            name = f"Stealth ({short})"
        elif "Acquired" in name:
            # "Almanax (Acquired)" — keep as published
            pass
        out.append(
            rec(
                name,
                "Gravity Labs",
                "Gravity Labs",
                description=desc,
                website=href.group(1) if href else "",
                date="Gravity Labs",
                verticals="Fintech; Blockchain",
                source_url=url,
                everywhere_tags=tag(name, desc, ["fintech", "crypto"]),
            )
        )
    return out


# ---- Defy VC ----
def defy():
    url = "https://defy.vc/companies/"
    s = get(url)
    out = []
    for part in re.split(r'class="company_row[^"]*"', s)[1:]:
        href = re.search(r'href="(https://defy\.vc/company/[^"]+)"', part)
        title_m = re.search(r'class="company_title">(.*?)</div>', part, re.S)
        bio_m = re.search(r'class="company_bio">(.*?)</div>', part, re.S)
        if not title_m:
            continue
        title_html = title_m.group(1)
        exit_m = re.search(r'class="exit_text">(.*?)</span>', title_html, re.S)
        exit_note = strip(exit_m.group(1)) if exit_m else ""
        name = strip(re.sub(r'<span class="exit_text">.*?</span>', "", title_html, flags=re.S))
        bio = strip(bio_m.group(1) if bio_m else "")
        if not name:
            continue
        desc = bio
        if exit_note:
            desc = (desc + f" (Exit: {exit_note})").strip() if desc else f"Exit: {exit_note}"
        page = (href.group(1).rstrip("/") + "/") if href else url
        out.append(
            rec(
                name,
                "Defy VC",
                "Defy VC",
                description=desc,
                date="Defy VC",
                source_url=page,
                everywhere_tags=tag(name, desc),
            )
        )
    # Enrich websites from a sample of company detail pages (official site links)
    def fetch_site(r):
        try:
            html = get(r["source_url"], timeout=30)
        except Exception:
            return r
        # Prefer explicit external company link that's not news
        cands = re.findall(r'href="(https?://(?!defy\.vc)[^"]+)"', html)
        skip = ("reuters.com", "forbes.com", "techcrunch", "fonts.", "google", "arkpes",
                "facebook.com", "twitter.com", "linkedin.com", "crunchbase", "pitchbook",
                "prnewswire", "finsmes", "fastcompany", "gmpg.org", "wp.com", "gravatar")
        for u in cands:
            low = u.lower()
            if any(x in low for x in skip):
                continue
            if re.search(r"\.(com|io|ai|co|app|net|org|xyz)(/|$)", low):
                r["website"] = u.split("?")[0]
                break
        return r

    with ThreadPoolExecutor(16) as ex:
        out = list(ex.map(fetch_site, out))
    enrich_from_sites(out)
    return out


# ---- Grishin Robotics ----
NAME_MAP = {
    "littlebits": "littleBits",
    "ring": "Ring",
    "eero": "eero",
    "spin": "Spin",
    "lfg": "LFG",
    "ziva": "Ziva Dynamics",
    "noise": "Noise",
    "squido": "Squido Studio",
    "a7": "Arctic7",
    "kadama": "Kadama",
    "skills": "The Skills",
    "roque": "Rogue",
    "taskade": "Taskade",
    "solid": "Solid",
    "club": "Club Feast",
    "zume": "Zume",
    "robotlab": "Robot Lab",
    "spire": "Spire",
    "zipline": "Zipline",
    "embodied": "Embodied",
    "starship": "Starship Technologies",
    "double": "Double Robotics",
    "occipital": "Occipital",
    "sphero": "Sphero",
    "bolt": "Bolt",
    "companies": "Swivl",  # filename quirk on their CMS
}


def grishinrobotics():
    url = "https://www.grishinrobotics.com/portfolio"
    s = get(url)
    out = []
    for p in re.split(r'class="item-company w-dyn-item"', s)[1:]:
        href_m = re.search(r'href="(https?://[^"]+)"', p)
        website = href_m.group(1) if href_m else ""
        img = re.search(r'<img[^>]+src="([^"]+)"', p)
        src = img.group(1) if img else ""
        fn = unquote(src.split("/")[-1].split("?")[0])
        fn = re.sub(r"^[0-9a-f]{8,}_", "", fn)
        fn = re.sub(r"\.(svg|png|jpg|jpeg|webp)$", "", fn, flags=re.I)
        fn = re.sub(r"(_svg|_png|_logo|-logo|\s*\(1\))$", "", fn, flags=re.I)
        key = fn.replace("-", " ").replace("_", " ").strip().lower().split()[0] if fn else ""
        # try full key
        key2 = re.sub(r"[^a-z0-9]+", "", fn.lower())
        name = NAME_MAP.get(key) or NAME_MAP.get(key2)
        if not name:
            # derive from website host
            if website:
                host = re.sub(r"^https?://(www\.)?", "", website).split("/")[0]
                name = host.split(".")[0]
                name = name[0].upper() + name[1:] if name else ""
            else:
                name = fn.replace("-", " ").replace("_", " ").strip()
        # description: first substantial text node
        desc = ""
        for m in re.finditer(r">([A-Za-z][^<]{8,100})<", p):
            t = strip(m.group(1))
            if t and "nth-child" not in t and "hover" not in t.lower() and "acquired by" not in t.lower():
                desc = t
                break
        acq = strip((re.search(r"(Acquired by [A-Za-z0-9 .,&\-]+)", p) or [None, ""])[1])
        if acq and acq.lower() != "acquired by":
            desc = f"{desc} ({acq})".strip() if desc else acq
        if not name:
            continue
        out.append(
            rec(
                name,
                "Grishin Robotics",
                "Grishin Robotics",
                description=desc,
                website=website,
                date="Grishin Robotics",
                verticals="Robotics",
                source_url=url,
                everywhere_tags=tag(name, desc, ["robotics", "hard tech"]),
            )
        )
    enrich_from_sites(out)
    return out


# ---- AGI House (portfolio array in frontend bundle) ----
def agihouse():
    home = get("https://www.agihouse.org/venture")
    # JS bundle path
    m = re.search(r'src="(/assets/index-[^"]+\.js)"', home)
    if not m:
        raise RuntimeError("AGI House: no JS bundle")
    js = get("https://www.agihouse.org" + m.group(1))
    # portfolio array near imgs/site/portfolio/
    recs = re.findall(r'name:"([^"]+)",tag:"([^"]*)",href:"([^"]+)"', js)
    seen = set()
    out = []
    for name, vert, href in recs:
        if name in seen or not href.startswith("http"):
            continue
        if name == "AGI House Labs":
            continue  # self
        seen.add(name)
        out.append(
            rec(
                name,
                "AGI House",
                "AGI House",
                description=vert,
                website=href,
                verticals=vert,
                date="AGI House Ventures",
                source_url="https://www.agihouse.org/venture",
                everywhere_tags=tag(name, vert, [vert]),
            )
        )
    return out


# ---- Long Beach Accelerator ----
def longbeachaccelerator():
    url = "https://www.lbaccelerator.org/portfolio/"
    s = get(url)
    out = []
    # h2 company names after "Accelerator Portfolio Companies"
    # Each company: <h2>Name</h2> ... <p>desc</p> ... <a href=site>
    # Skip section headers
    skip = {"Cohort Spotlight", "Accelerator Portfolio Companies"}
    for m in re.finditer(
        r'<div class="the-content p-logo__txt-box">\s*<h2>(.*?)</h2>(.*?)</div>\s*</div>',
        s,
        re.S,
    ):
        name = strip(m.group(1))
        body = m.group(2)
        if not name or name in skip:
            continue
        desc = strip((re.search(r"<p>(.*?)</p>", body, re.S) or [None, ""])[1])
        href = re.search(r'href="(https?://[^"]+)"', body)
        out.append(
            rec(
                name,
                "Long Beach Accelerator",
                "Long Beach Accelerator",
                description=desc,
                website=href.group(1) if href else "",
                date="Long Beach Accelerator",
                source_url=url,
                everywhere_tags=tag(name, desc),
            )
        )
    if not out:
        # fallback: h2 list after portfolio header
        h2s = [strip(x) for x in re.findall(r"<h2[^>]*>(.*?)</h2>", s, re.S)]
        started = False
        for n in h2s:
            if n == "Accelerator Portfolio Companies":
                started = True
                continue
            if not started or n in skip:
                continue
            out.append(
                rec(n, "Long Beach Accelerator", "Long Beach Accelerator",
                    date="Long Beach Accelerator", source_url=url)
            )
    enrich_from_sites(out)
    return out


# ---- Alchemist (public vault API used by portfolio page) ----
def alchemist():
    api = "https://vault.alchemistaccelerator.com/api/v1/alchemist_companies"
    params = {
        "include": "aclass",
        "fields[alchemist_classes]": "number",
        "filter[aclass.class_type:eq]": "alchemist",
        "page[size]": "100",
    }
    out = []
    for page in range(1, 50):
        params["page[number]"] = str(page)
        r = SESSION.get(api, params=params, timeout=60)
        r.raise_for_status()
        data = r.json().get("data") or []
        for c in data:
            attrs = c.get("attributes") or {}
            meta = c.get("meta") or {}
            name = attrs.get("name") or ""
            if not name:
                continue
            desc = clean(meta.get("oneliner") or "") or clean(
                (meta.get("description") or "").split("\n")[0]
            )[:400]
            team = clean(meta.get("startup_teamdescription") or "")
            # team often multi-line founders — compress
            team = re.sub(r"\s+", " ", team)[:200]
            slug = meta.get("slug") or ""
            source_url = (
                f"https://vault.alchemistaccelerator.com/companies/public/{slug}"
                if slug
                else "https://www.alchemistaccelerator.com/portfolio"
            )
            aclass = meta.get("aclass_id")
            date = f"Alchemist Class {aclass}" if aclass else "Alchemist"
            raised = meta.get("startup_totalraise")
            amount = f"${raised:,.0f}" if isinstance(raised, (int, float)) and raised else ""
            rnd = clean(meta.get("last_round_stage") or "")
            loc = clean(meta.get("location_formatted_address") or "")
            status = clean(meta.get("status") or "")
            out.append(
                rec(
                    name,
                    "Alchemist Accelerator",
                    "Alchemist",
                    description=desc,
                    team=team,
                    date=date,
                    amount_raised=amount,
                    round=rnd if rnd in {"Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Series D", "Series E", "Growth"} else "",
                    source_url=source_url,
                    location=loc,
                    status=status,
                    everywhere_tags=tag(name, desc),
                )
            )
        if len(data) < 100:
            break
    enrich_from_sites(out)
    return out


# ---- Entrepreneurs First ----
def entrepreneursfirst():
    url = "https://www.joinef.com/portfolio/"
    s = get(url)
    out = []
    # Each tile
    for block in re.split(r'class="tile tile--company[^"]*"', s)[1:]:
        name = strip((re.search(r'tile__name[^>]*>\s*(?:<span[^>]*>)?(.*?)(?:</span>)?\s*</h4>', block, re.S) or [None, ""])[1])
        if not name:
            name = strip((re.search(r'tile__name[^>]*>(.*?)</h4>', block, re.S) or [None, ""])[1])
            name = strip(re.sub(r"<[^>]+>", " ", name))
        desc = strip((re.search(r'tile__description[^>]*>(.*?)</div>', block, re.S) or [None, ""])[1])
        locs = [strip(x) for x in re.findall(r"locationtag[^>]*>(.*?)</a>", block, re.S)]
        cats = [strip(x) for x in re.findall(r"categorytag[^>]*>(.*?)</a>", block, re.S)]
        # company page link
        link = re.search(r'href="(https://www\.joinef\.com/compan(?:y|ies)/[^"]+)"', block)
        if not name:
            continue
        out.append(
            rec(
                name,
                "Entrepreneurs First",
                "Entrepreneurs First",
                description=desc,
                verticals="; ".join(cats),
                date="EF",
                location="; ".join(locs),
                source_url=link.group(1) if link else url,
                everywhere_tags=tag(name, desc, cats),
            )
        )
    # Try to get websites from EF company pages (official)
    def fetch_site(r):
        if not r.get("source_url") or "joinef.com" not in r["source_url"]:
            return r
        try:
            html = get(r["source_url"], timeout=30)
        except Exception:
            return r
        # outbound company website
        for u in re.findall(r'href="(https?://(?!www\.joinef\.com)[^"]+)"', html):
            low = u.lower()
            if any(x in low for x in ("facebook", "twitter", "linkedin", "instagram", "youtube",
                                       "crunchbase", "pitchbook", "google.com", "apple.com")):
                continue
            if re.search(r"\.(com|io|ai|co|app|net|org|uk|so|dev)(/|$)", low):
                r["website"] = u.split("?")[0]
                break
        return r

    with ThreadPoolExecutor(12) as ex:
        out = list(ex.map(fetch_site, out))
    enrich_from_sites(out)
    return out


# ---- Seedcamp ----
VERT_MAP = {
    "ai": "AI",
    "climate": "Climate",
    "consumer": "Consumer",
    "crypto": "Crypto",
    "developer-tools": "Developer Tools",
    "enterprise": "Enterprise",
    "fintech": "Fintech",
    "health-bio": "Health/Bio",
    "marketplaces": "Marketplaces",
    "security": "Security",
}


def seedcamp():
    url = "https://seedcamp.com/our-companies/"
    s = get(url)
    out = []
    for m in re.finditer(
        r'class="company__item mix ([^"]*)"[^>]*>(.*?)(?=class="company__item mix|$)',
        s,
        re.S,
    ):
        mix, block = m.group(1), m.group(2)
        name = strip(
            (re.search(r'company__item__name[^>]*>(.*?)</span>', block, re.S) or [None, ""])[1]
        )
        name = strip(re.sub(r"<[^>]+>", " ", name))
        year = strip((re.search(r'company__item__year[^>]*>(.*?)</', block, re.S) or [None, ""])[1])
        desc = strip(
            (re.search(r'company__item__description__content[^>]*>(.*?)</div>', block, re.S)
             or [None, ""])[1]
        )
        link = re.search(r'<a href="(https?://[^"]+)"[^>]*class="[^"]*company__item__link', block)
        if not link:
            link = re.search(r'href="(https?://(?!seedcamp\.com)[^"]+)"', block)
        if not name:
            continue
        verts = [VERT_MAP.get(x, x) for x in mix.split() if x and x != "mix"]
        out.append(
            rec(
                name,
                "Seedcamp",
                "Seedcamp",
                description=desc,
                website=link.group(1) if link else "",
                date=f"Seedcamp {year}" if year else "Seedcamp",
                verticals="; ".join(verts),
                source_url=url,
                everywhere_tags=tag(name, desc, verts),
            )
        )
    enrich_from_sites(out)
    return out


# ---- Founders Factory ----
def foundersfactory():
    url = "https://foundersfactory.com/portfolio/"
    s = get(url)
    out = []
    seen = set()
    # Featured grid from page-data (names + links)
    try:
        pd = SESSION.get(
            "https://foundersfactory.com/page-data/portfolio/page-data.json", timeout=60
        ).json()
        content = json.loads(pd["result"]["pageContext"]["story"]["content"])
        for block in content.get("body") or []:
            if block.get("component") != "FeaturedCompaniesGridSection":
                continue
            for card in block.get("cards") or []:
                name = clean(card.get("companyName") or "")
                link = (card.get("link") or {}).get("url") or (card.get("link") or {}).get("cached_url") or ""
                if name and name not in seen:
                    seen.add(name)
                    out.append(
                        rec(
                            name,
                            "Founders Factory",
                            "Founders Factory",
                            website=link if link.startswith("http") else "",
                            date="Founders Factory",
                            source_url=url,
                            everywhere_tags=tag(name, ""),
                        )
                    )
    except Exception as e:
        print("FF page-data featured warn:", e)

    # Filter grid cards in SSR HTML: h3 name + p desc + Visit site link
    for m in re.finditer(
        r'<h3 class="[^"]*text-\[24px\][^"]*"[^>]*>(.*?)</h3>\s*'
        r'<div class="h-\[116px\]"><p[^>]*>(.*?)</p></div>\s*'
        r'<div class="[^"]*"><a href="(https?://[^"]+)"[^>]*title="([^"]*)"',
        s,
        re.S,
    ):
        name, desc, website, title = strip(m.group(1)), strip(m.group(2)), m.group(3), strip(m.group(4))
        name = name or title
        if not name or name in seen:
            # update desc if we already have from featured
            if name in seen:
                for r in out:
                    if r["name"] == name and desc and not r.get("description"):
                        r["description"] = desc
                        if website and not r.get("website"):
                            r["website"] = website
                        r["everywhere_tags"] = tag(name, desc)
            continue
        # sector label just above h3
        seen.add(name)
        out.append(
            rec(
                name,
                "Founders Factory",
                "Founders Factory",
                description=desc,
                website=website,
                date="Founders Factory",
                source_url=url,
                everywhere_tags=tag(name, desc),
            )
        )

    # Broader fallback for cards
    if len(out) < 20:
        for m in re.finditer(
            r'<h3[^>]*>([^<]+)</h3>\s*<div[^>]*>\s*<p[^>]*>(.*?)</p>\s*</div>.*?'
            r'href="(https?://(?!foundersfactory\.com)[^"]+)"[^>]*title="\1"',
            s,
            re.S,
        ):
            name, desc, website = strip(m.group(1)), strip(m.group(2)), m.group(3)
            if name.startswith("Filter") or name in seen:
                continue
            seen.add(name)
            out.append(
                rec(name, "Founders Factory", "Founders Factory", description=desc,
                    website=website, date="Founders Factory", source_url=url,
                    everywhere_tags=tag(name, desc))
            )
    enrich_from_sites(out)
    return out


REG = {
    "launch": launch,
    "gravitylabs": gravitylabs,
    "defy": defy,
    "grishinrobotics": grishinrobotics,
    "agihouse": agihouse,
    "longbeachaccelerator": longbeachaccelerator,
    "alchemist": alchemist,
    "entrepreneursfirst": entrepreneursfirst,
    "seedcamp": seedcamp,
    "foundersfactory": foundersfactory,
}


if __name__ == "__main__":
    slugs = sys.argv[1:] or list(REG)
    for slug in slugs:
        print(f"=== scraping {slug} ===")
        recs = dedupe(REG[slug]())
        save(slug, recs, {"source_fn": slug})
