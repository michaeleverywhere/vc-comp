"""Replace 'website' values that are accelerator profile pages with the company's external
website published on that profile page; strip utm_* params. Clear if none is published."""
import json, os, re, sys
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import requests
from common import DATA_DIR, UA, norm_name, norm_linkedin, LI_RE
ACC = re.compile(r"seraphim\.vc|ycombinator\.com|pear\.vc", re.I)
SKIP = re.compile(r"seraphim\.vc|ycombinator\.com|pear\.vc|twitter\.com|x\.com|facebook|instagram|youtube|"
                  r"linkedin|crunchbase|pitchbook|google|apple\.com|wordpress|wp\.com|gravatar|w3\.org|"
                  r"schema\.org|cloudflare|jsdelivr|gstatic|hubspot|typekit|vimeo|medium\.com|github\.com", re.I)
def strip_utm(u):
    s = urlsplit(u); q = [(k, v) for k, v in parse_qsl(s.query) if not k.lower().startswith("utm_")]
    return urlunsplit((s.scheme, s.netloc, s.path, urlencode(q), ""))
for slug in sys.argv[1:]:
    p = os.path.join(DATA_DIR, f"{slug}_companies.json"); d = json.load(open(p))
    for r in d["companies"]:
        w = r.get("website") or ""
        if "utm_" in w:
            r["website"] = strip_utm(w)
        if not ACC.search(urlsplit(w).netloc) or r["name"] == "Y Combinator":
            continue
        try:
            s = requests.get(w, headers=UA, timeout=20).text
        except Exception:
            s = ""
        toks = [norm_name(t) for t in re.split(r"[\s.\-]+", r["name"]) if len(norm_name(t)) >= 3]
        cands = [h for h in re.findall(r'href=["\'](https?://[^"\']+)', s) if not SKIP.search(urlsplit(h).netloc)]
        hit = next((h for h in cands if any(t in norm_name(urlsplit(h).netloc) for t in toks)), "")
        new = strip_utm(hit) if hit else ""
        if not r.get("linkedin_url"):
            for m in LI_RE.finditer(s):
                li = norm_linkedin(m.group(0))
                if "/company/" in li and any(t in norm_name(li) for t in toks):
                    r["linkedin_url"], r["linkedin_source"] = li, "accelerator profile page"; break
        print(slug, r["name"], w, "->", new or "(none published)", "| li", r.get("linkedin_url", ""))
        r["website"] = new
        r["website_source"] = "accelerator profile page" if new else ""
    json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
