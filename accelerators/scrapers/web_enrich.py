"""Find official websites for companies with no website, without Crunchbase/LinkedIn/PitchBook.
1) Wikidata (P856 official website) for an entity whose label matches the name and whose
   description says company/startup/business/software.
2) Candidate domains built from the name (name.com/.ai/.io/.co/.xyz, try/get/use/hello+name.com).
A candidate is accepted only if the fetched page (a) is not an accelerator/banned/parking host,
(b) carries the compact company name in its <title>/og:site_name or domain, and
(c) when we already have an accelerator description, shares >=2 content words with the site's
    own meta/title text (guards against same-name companies).
Then fills a blank description from the site meta description and the LinkedIn link the site
itself publishes. Records website_source / description_source."""
import html as _h, json, os, re, sys, warnings
from concurrent.futures import ThreadPoolExecutor
import requests
from common import DATA_DIR, UA, BANNED, clean, norm_name, tag, LI_RE, norm_linkedin
warnings.filterwarnings("ignore")
ACC = re.compile(r"seraphim\.vc|ycombinator\.com|techstars\.com|sosv\.com|hax\.co|pear\.vc|catalystaccelerator|"
                 r"betaworks\.com|southparkcommons\.com|zfellows\.com|hf0\.com|wikipedia|wikidata|"
                 r"godaddy|sedo|dan\.com|afternic|hugedomains|namecheap|squarespace\.com/domain|parking|"
                 r"domain(s)? for sale|bodis|above\.com", re.I)
STOP = set("the and for with that your from into our are you all its their this a an of to in on by is we "
           "platform company startup build building helps help make makes using based new best world".split())
def words(s):
    return {w for w in re.findall(r"[a-z]{4,}", (s or "").lower()) if w not in STOP}

def fetch(u):
    try:
        r = requests.get(u, headers=UA, timeout=12, allow_redirects=True, verify=False)
        if "charset" not in r.headers.get("content-type", "").lower():
            r.encoding = r.apparent_encoding
        if r.status_code >= 400 or BANNED.search(r.url) or ACC.search(r.url):
            return None, None
        return r.url, r.text[:400000]
    except Exception:
        return None, None

def meta(s, key):
    for pat in (rf'<meta[^>]+(?:name|property)=["\']{key}["\'][^>]*content=["\']([^"\']+)',
                rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]*(?:name|property)=["\']{key}["\']'):
        m = re.search(pat, s, re.I)
        if m:
            return clean(_h.unescape(m.group(1)))
    return ""

def verify(url, s, name, known_desc):
    if not s or re.search(r"for sale|buy this domain|parked|this domain|coming soon|domain names?\b|make an offer", s[:20000], re.I):
        return False, ""
    title = clean(_h.unescape((re.search(r"<title[^>]*>(.*?)</title>", s, re.I | re.S) or [None, ""])[1]))
    site = meta(s, "og:site_name")
    cn = norm_name(name)
    host = norm_name(re.sub(r"^www\.", "", re.match(r"https?://([^/]+)", url).group(1)).split(".")[0])
    if len(cn) < 3 or not (cn in norm_name(title + " " + site) or cn == host or (len(cn) >= 5 and cn in host)):
        return False, ""
    d = meta(s, "description") or meta(s, "og:description")
    if known_desc:
        head = words(title + " " + d + " " + meta(s, "og:description") + " " + meta(s, "og:title"))
        body = words(re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s[:200000], flags=re.S)))
        kw = words(known_desc) - words(name)
        if not (len(kw & head) >= 2 or (len(kw & head) >= 1 and len(kw & body) >= 4)):
            return False, ""
    return True, d

def wikidata(name):
    try:
        r = requests.get("https://www.wikidata.org/w/api.php", params={"action": "wbsearchentities", "search": name,
                         "language": "en", "format": "json", "limit": 5, "type": "item"}, headers=UA, timeout=12).json()
        for e in r.get("search", []):
            if norm_name(e.get("label", "")) != norm_name(name):
                continue
            if not re.search(r"compan|startup|business|software|manufactur|firm|service|platform|developer|brand",
                             e.get("description", ""), re.I):
                continue
            c = requests.get(f"https://www.wikidata.org/wiki/Special:EntityData/{e['id']}.json", headers=UA, timeout=12).json()
            cl = c["entities"][e["id"]]["claims"]
            for st in cl.get("P856", []):
                v = st["mainsnak"].get("datavalue", {}).get("value")
                if v:
                    return v, f"https://www.wikidata.org/wiki/{e['id']}"
    except Exception:
        pass
    return "", ""

def candidates(name):
    base = re.sub(r"\s*\(.*?\)", "", name)
    c1 = re.sub(r"[^a-z0-9]", "", base.lower())
    c2 = re.sub(r"[^a-z0-9-]", "", re.sub(r"\s+", "-", base.lower().strip()))
    out = []
    for c in dict.fromkeys([c1, c2]):
        if len(c) < 3:
            continue
        out += [f"https://{c}.{t}" for t in ("com", "ai", "io", "co", "xyz", "so", "dev", "app")]
        out += [f"https://{p}{c}.com" for p in ("try", "get", "use", "hello", "join")]
        out += [f"https://{c}hq.com", f"https://{c}.inc", f"https://{c}labs.com"]
    return out

def find(r):
    name, kd = r["name"], r.get("description") or ""
    w, src = wikidata(name)
    if w:
        u, s = fetch(w)
        if u:
            ok, d = verify(u, s, name, "") if not kd else verify(u, s, name, kd)
            if ok or not kd:   # Wikidata's official-website claim is itself a reputable source
                return w, f"Wikidata official website ({src})", (d if ok else meta(s, "description")), s
    for c in candidates(name):
        u, s = fetch(c)
        if not u:
            continue
        ok, d = verify(u, s, name, kd)
        if ok:
            return re.match(r"https?://[^/]+", u).group(0) + "/", "company website (domain verified against name" + \
                   (" and accelerator description)" if kd else ")"), d, s
    return "", "", "", ""

def run(slug, only_missing=True):
    p = os.path.join(DATA_DIR, f"{slug}_companies.json"); D = json.load(open(p)); R = D["companies"]
    todo = [r for r in R if not r.get("website")]
    before = (sum(1 for r in R if r.get("website")), sum(1 for r in R if r.get("description")))
    with ThreadPoolExecutor(12) as ex:
        res = list(ex.map(find, todo))
    for r, (w, src, d, s) in zip(todo, res):
        if not w:
            continue
        r["website"], r["website_source"] = w, src
        if not r.get("description") and d and len(d.split()) >= 3:
            r["description"], r["description_source"] = d, "company website meta description"
        if not r.get("linkedin_url"):
            m = LI_RE.search(s or "")
            if m and "/company/" in m.group(0):
                r["linkedin_url"], r["linkedin_source"] = norm_linkedin(m.group(0)), "company website"
        if not r.get("everywhere_tags") and r.get("description"):
            r["everywhere_tags"] = tag(r["name"], r["description"], [x for x in (r.get("verticals") or "").split("; ") if x])
    json.dump(D, open(p, "w"), indent=1, ensure_ascii=False)
    after = (sum(1 for r in R if r.get("website")), sum(1 for r in R if r.get("description")))
    print(slug, "rows", len(R), "website", before[0], "->", after[0], "desc", before[1], "->", after[1], flush=True)
    for r, (w, src, d, s) in zip(todo, res):
        if w: print("  ", r["name"], w, "|", src[:40])

if __name__ == "__main__":
    for s in sys.argv[1:]:
        run(s)
