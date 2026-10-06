"""Idempotent REST upsert into Accelerator Data (match on Name + Investors).

Usage: AIRTABLE_PAT=... python accelerators/airtable_upsert.py <slug>...
Needs a PAT with data.records:write on base appdSRg0657zG3oef. typecast=true so
new Source choices (e.g. "YC") are created on first write.
"""
import os
import sys
import time

import requests

from airtable_rows import rows

BASE, TABLE = "appdSRg0657zG3oef", "tblM2JO3HToYoV1Bi"


def upsert(slug):
    url = f"https://api.airtable.com/v0/{BASE}/{TABLE}"
    h = {"Authorization": f"Bearer {os.environ['AIRTABLE_PAT']}", "Content-Type": "application/json"}
    rs, n = rows(slug), 0
    for i in range(0, len(rs), 10):
        body = {"performUpsert": {"fieldsToMergeOn": ["Name", "Investors"]}, "typecast": True,
                "records": [{"fields": r} for r in rs[i:i + 10]]}
        for attempt in range(5):
            resp = requests.patch(url, headers=h, json=body, timeout=60)
            if resp.status_code != 429:
                break
            time.sleep(30)
        resp.raise_for_status()
        n += len(body["records"])
        time.sleep(0.22)   # stay under 5 req/s
    print(f"[{slug}] upserted {n}")
    return n


if __name__ == "__main__":
    for s in sys.argv[1:]:
        upsert(s)
