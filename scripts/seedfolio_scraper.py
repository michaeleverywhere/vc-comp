#!/usr/bin/env python3
"""seedfolio portfolio scraper.

Source: https://www.seedfolio.vc/portfolio — Seed-stage biotech/deeptech portfolio (Seedfolio).
"""
from __future__ import annotations
import json
from pathlib import Path
from _d50_common import rec, finish

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "seedfolio_companies.json"


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
                "Seedfolio",
                "https://www.seedfolio.vc/portfolio",
                "2026-10-26",
            )
        )
    finish(out, "seedfolio", ["company_name"])


if __name__ == "__main__":
    main()
