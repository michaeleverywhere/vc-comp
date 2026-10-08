"""2026-10-08 list1/list2 backfill.
- LAUNCH: add cohort companies LA26-LA36 published on launchaccelerator.co (cohort data embedded
  in the site's JS bundle, rendered on /companies and /36 "Yearbook"); keeps the 19 launch.co logos.
- Invest Ottawa (IO Accelerator): investottawa.ca/io-accelerator-companies/ (current + graduates);
  missing/wrong websites fixed from the logo links on investottawa.ca/venture-path/accelerator/;
  descriptions = company site meta description.
- Astera Institute Residency: astera.org/residency/ residents + alumni (project + bio from
  astera.org/resident/<slug>/).
Tags: keyword classifier only (automation/tags.py). No LinkedIn/Crunchbase/PitchBook."""
import html, json, os, re, subprocess, sys, time
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA_DIR, UA, tags

def get(u, t=20):
    try:
        r = requests.get(u, headers=UA, timeout=t, allow_redirects=True)
        return r.text if r.status_code == 200 else ""
    except Exception:
        return ""

def meta_desc(u):
    s = get(u, 15)
    for pat in [r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description',
                r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)']:
        m = re.search(pat, s, re.I)
        if m:
            d = " ".join(html.unescape(m.group(1)).split())
            if len(d) > 25:
                return d
    return ""

def rec(**k):
    base = dict(name="", description="", website="", team="", round="", amount_raised="", date="",
                verticals="", investors="", source="", everywhere_tags=[], source_url="", linkedin_url="",
                batch_date="", batch_date_precision="", location="", most_recent_batch=False)
    base.update(k)
    if not base["everywhere_tags"]:
        base["everywhere_tags"] = tags.classify(base["name"], base["description"], base["verticals"] or None)
    return base

def save(slug, cs, extra=None):
    D = {"accelerator": slug, "count": len(cs), "source_fn": slug, **(extra or {}), "companies": cs}
    json.dump(D, open(os.path.join(DATA_DIR, f"{slug}_companies.json"), "w"), ensure_ascii=False, indent=1)
    print(slug, len(cs))

def launch():
    home = get("https://launchaccelerator.co/")
    js = re.search(r'src="(/assets/index-[^"]+\.js)"', home).group(1)
    s = get("https://launchaccelerator.co" + js, 60)
    st = s.find('{id:"la36",label:"LA36"')
    k = s.rfind("[", 0, st)
    depth, i = 0, k
    while True:
        c = s[i]
        if c == "[": depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0: break
        elif c == '"':
            i += 1
            while s[i] != '"':
                if s[i] == "\\": i += 1
                i += 1
        i += 1
    open("/tmp/la_cohorts.js", "w").write("module.exports=" + s[k:i + 1])
    cohorts = json.loads(subprocess.check_output(["node", "-e", 'process.stdout.write(JSON.stringify(require("/tmp/la_cohorts.js")))']))
    P = os.path.join(DATA_DIR, "launch_companies.json")
    old = json.load(open(P))["companies"]
    seen = {o["name"].lower() for o in old}
    out = list(old)
    for co in cohorts:
        lab = co["label"]
        for c in co["companies"]:
            if c["name"].lower() in seen:
                continue
            seen.add(c["name"].lower())
            latest = lab == "LA36"
            out.append(rec(name=c["name"], description=c.get("description", ""), website=c.get("website", ""),
                           date=f"LAUNCH {lab}", investors="LAUNCH Accelerator", source="LAUNCH",
                           source_url="https://launchaccelerator.co/companies" if not latest else "https://launchaccelerator.co/36",
                           batch_date="2026-06-09" if latest else "", batch_date_precision="day (Demo Day)" if latest else "",
                           most_recent_batch=latest))
    save("launch", out)

def investottawa():
    s = get("https://www.investottawa.ca/io-accelerator-companies/")
    acc = get("https://www.investottawa.ca/venture-path/accelerator/")
    links = {}
    for u, a in re.findall(r'<a [^>]*href="(https?://[^"]+)"[^>]*>\s*<img [^>]*alt="([^"]*)"', acc):
        a = html.unescape(a).replace(" logo", "").replace(" Logo", "").strip().lower()
        if a and "investottawa" not in u:
            links[a] = u
    alias = {"gamestrat": "game strat", "hyperion": "hyperion global energy", "smats": "smats", "stripe": "stripe studio"}
    main = s[s.find("<main"):s.find("</main>")]
    out, section = [], "IO Accelerator (current)"
    seen_sites = {}
    for m in re.finditer(r'(<p class="impact__heading">(.*?)</p>|<h[23][^>]*>(.*?)</h[23]>|<div class="cell [^"]*">(.*?)<h4 class="company-hover-text">(.*?)</h4>)', main, re.S):
        if m.group(2) or m.group(3):
            t = html.unescape(re.sub("<[^>]+>", "", m.group(2) or m.group(3))).strip()
            if "Graduates" in t: section = "IO Accelerator Graduate"
            continue
        name = html.unescape(m.group(5)).strip()
        w = re.search(r'<a href="([^"]+)"', m.group(4))
        site = w.group(1) if w else ""
        out.append([name, site, section])
    # site's own copy-paste errors: duplicate URLs on two different companies -> prefer the logo-strip link, else blank
    from collections import Counter
    dup = Counter(x[1] for x in out if x[1])
    for x in out:
        key = alias.get(x[0].lower(), x[0].lower())
        if (not x[1] or dup[x[1]] > 1) and key in links:
            x[1] = links[key]
    dup = Counter(x[1] for x in out if x[1])
    cs = []
    for name, site, section in out:
        if site and dup[site] > 1:
            # keep only for the company whose name matches the domain
            dom = re.sub(r"^https?://(www\.)?", "", site).split("/")[0].split(".")[0]
            if dom.replace("-", "") not in name.lower().replace(" ", ""):
                site = ""
        d = meta_desc(site) if site else ""
        time.sleep(0.3)
        cs.append(rec(name=name, description=d, website=site, date=section, investors="Invest Ottawa (IO Accelerator)",
                      source="Invest Ottawa", source_url="https://www.investottawa.ca/io-accelerator-companies/",
                      location="Ottawa, ON, Canada", most_recent_batch=section.endswith("(current)"),
                      **({"description_source": "company site meta description"} if d else {})))
    save("investottawa", cs)

def astera():
    s = get("https://astera.org/residency/")
    i = s.find("Astera Residents"); body = s[i:]
    am = re.search(r">\s*Alumni\s*<", body)
    alum_at = am.start() if am else -1
    cs = []
    for m in re.finditer(r'href="(https://astera.org/resident/[^"]+/)"', body):
        url = m.group(1)
        if any(c["source_url"] == url for c in cs):
            continue
        p = get(url)
        p2 = re.sub(r"<script.*?</script>|<style.*?</style>|<svg.*?</svg>", "", p, flags=re.S)
        L = [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", p2)).split("\n") if l.strip()]
        title = re.search(r"<title>(.*?) - Astera</title>", p).group(1).strip()
        j = max(k for k, l in enumerate(L) if l == title)
        project, bio = L[j + 1], (L[j + 2] if j + 2 < len(L) else "")
        alumni = alum_at >= 0 and m.start() > alum_at
        first = re.split(r"(?<!\bDr\.)(?<!\bMr\.)(?<!\bMs\.)(?<=\.)\s", bio)[0]
        prev = next((c for c in cs if c["name"] == project), None)
        if prev:  # two residents on one project -> one row
            first_lead = prev["team"]
            prev["team"] += f"; {title}"
            prev["description"] = prev["description"].replace(f" led by {first_lead}.", f" led by {first_lead} and {title}.", 1)
            prev.setdefault("resident_urls", []).append(url)
            continue
        cs.append(rec(name=project, description=f"{project}: Astera Residency project led by {title}. {first}".strip(),
                      team=title, date="Astera Residency (alumni)" if alumni else "Astera Residency (current)",
                      investors="Astera Institute (Residency)", source="Astera", source_url=url,
                      location="Emeryville, CA, USA", most_recent_batch=not alumni,
                      notes="Residency funds open public-goods projects (people/projects, not necessarily companies)."))
        time.sleep(0.3)
    save("astera", cs)

if __name__ == "__main__":
    for f in sys.argv[1:]:
        globals()[f]()
