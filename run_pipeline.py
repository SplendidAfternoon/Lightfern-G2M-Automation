#!/usr/bin/env python3
"""
Lightfern Champion GTM Pipeline — single entry point.

  Unify (API or audience CSV) -> Champion Scorer -> Zero CRM
  Scaile keyword sync (inbound tracking)

Usage:
  python run_pipeline.py
  python run_pipeline.py --dry-run
  python run_pipeline.py --skip-zero
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from integrations.scaile_client import run_scaile_sync
from integrations.unify_client import pull_audience
from integrations.zero_client import list_contacts, push_csv


def run_scorer() -> int:
    result = subprocess.run([sys.executable, str(ROOT / "score_prospects.py")], cwd=ROOT)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full Lightfern champion GTM pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Preview Zero push only")
    parser.add_argument("--skip-zero", action="store_true")
    parser.add_argument("--skip-scaile", action="store_true")
    parser.add_argument("--skip-unify", action="store_true")
    args = parser.parse_args()

    print("=" * 72)
    print("LIGHTFERN CHAMPION GTM PIPELINE")
    print("=" * 72)

    # Step 1: Unify -> data/unify_contacts.csv
    if not args.skip_unify:
        print("\n[1/4] Pull from Unify (API -> CSV fallback)...")
        contacts, source = pull_audience(ROOT / "data" / "unify_contacts.csv", data_dir=ROOT / "data")
        print(f"      {len(contacts)} contacts | source: {source}")
        if "empty" in source or "fallback" in source:
            print("      NOTE: Unify Data API has 0 person records — using audience CSV exports in data/")
    else:
        print("\n[1/4] Skipped Unify pull")

    # Step 2: Score
    print("\n[2/4] Champion Scorer...")
    if run_scorer() != 0:
        print("Scorer failed", file=sys.stderr)
        return 1

    leaderboard = ROOT / "output" / "scored_leaderboard.csv"
    if not leaderboard.exists():
        print("Missing scored_leaderboard.csv", file=sys.stderr)
        return 1

    # Step 3: Zero CRM
    if not args.skip_zero:
        print("\n[3/4] Push to Zero CRM (Tier A + Tier B)...")
        created, skipped, failed = push_csv(
            leaderboard,
            tiers=["Tier A", "Tier B"],
            dry_run=args.dry_run,
            skip_existing=True,
        )
        print(f"      {created} created, {skipped} skipped (already in Zero), {failed} failed")
        if not args.dry_run:
            in_zero = [c for c in list_contacts(200) if c.get("source") == "lightfern_champion_scorer"]
            print(f"      Total lightfern_champion_scorer contacts in Zero: {len(in_zero)}")
            print("      View in Zero: filter by source = lightfern_champion_scorer")
    else:
        print("\n[3/4] Skipped Zero push")

    # Step 4: Scaile
    if not args.skip_scaile:
        print("\n[4/4] Scaile inbound sync...")
        result = run_scaile_sync()
        print(f"      {json.dumps(result, indent=2)}")
    else:
        print("\n[4/4] Skipped Scaile sync")

    print("\n" + "=" * 72)
    print("OUTPUTS:")
    print(f"  Scored:   output/scored_leaderboard.csv")
    print(f"  Tier A:   output/tier_a_unify_export.csv  (import to Unify sequences)")
    print(f"  Zero:     output/zero_import.csv")
    print(f"  Inbound:  inbound/scaile_tracking.csv")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
