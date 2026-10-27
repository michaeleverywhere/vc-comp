#!/usr/bin/env python3
"""ballastpointventures portfolio scraper.

Source: https://ballastpointpartners.com/our-companies/ — Southeast growth/venture portfolio (Ballast Point Ventures).
"""
from __future__ import annotations
import json
from pathlib import Path
from _d50_common import rec, finish

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "ballastpointventures_companies.json"


def main() -> None:
    raw = json.loads(SRC.read_text())
    out = []
    for r in raw:
        name = (r.get("company_name") or "").strip()
        if not name:
            continue
        out.append(
            rec(
                name,
                None,
                r.get("company_url"),
                "Ballast Point Ventures",
                "https://ballastpointpartners.com/our-companies/",
                "2026-10-26",
            )
        )
    finish(out, "ballastpointventures", ["company_name"])


if __name__ == "__main__":
    main()
