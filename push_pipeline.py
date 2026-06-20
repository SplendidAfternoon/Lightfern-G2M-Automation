#!/usr/bin/env python3
"""Push scored leaderboard to Zero CRM — use run_pipeline.py for full chain."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from integrations.zero_client import push_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Push scored contacts to Zero CRM")
    parser.add_argument("--csv", default="output/scored_leaderboard.csv")
    parser.add_argument("--tier", default="A,B", help="A,B or all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    csv_path = root / args.csv
    if not csv_path.exists():
        print(f"Missing {csv_path} — run score_prospects.py first", file=sys.stderr)
        return 1

    if args.tier.lower() == "all":
        tiers = ["Tier A", "Tier B", "Reject"]
    else:
        mapping = {"A": "Tier A", "B": "Tier B", "R": "Reject"}
        tiers = [mapping.get(p.strip(), p.strip()) for p in args.tier.split(",")]

    created, skipped, failed = push_csv(csv_path, tiers=tiers, dry_run=args.dry_run)
    print(f"Zero CRM: {created} created, {skipped} skipped, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
