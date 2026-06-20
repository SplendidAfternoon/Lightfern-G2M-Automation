"""Scaile — inbound visibility tracking.

Scaile dashboard tracks keywords from setup forward (no historical scores on day 1).
This client:
  1. Registers/monitors keywords from config
  2. Syncs inbound/scaile_tracking.csv
  3. Attempts API calls when SCAILE_API_BASE is reachable

Note: api.scaile.tech may not resolve publicly; baseline lives in scaile_baseline.md.
"""

from __future__ import annotations

import csv
import json
import os
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

DEFAULT_BASE = os.environ.get("SCAILE_API_BASE", "https://api.scaile.tech")


def _load_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def _headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def try_api_get(path: str) -> tuple[bool, Any]:
    _load_env()
    key = os.environ.get("SCAILE_API_KEY", "")
    if not key:
        return False, "SCAILE_API_KEY not set"
    base = os.environ.get("SCAILE_API_BASE", DEFAULT_BASE)
    url = f"{base.rstrip('/')}{path}"
    req = urllib.request.Request(url, headers=_headers(key))
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read()[:200].decode(errors='replace')}"
    except Exception as e:
        return False, str(e)


def sync_tracking_csv(
    tracking_path: Path,
    keywords: list[str],
    baseline_rows: list[dict[str, str]] | None = None,
) -> None:
    """Ensure tracking CSV has one row per keyword for current week."""
    tracking_path.parent.mkdir(parents=True, exist_ok=True)
    week = date.today().strftime("%Y-W%W")

    existing: dict[str, dict[str, str]] = {}
    if tracking_path.exists():
        with tracking_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                existing[row.get("search_term", "")] = row

    fieldnames = [
        "week", "search_term", "lightfern_mentioned", "top_competitors",
        "visibility_notes", "content_piece", "action", "scaile_api_status",
    ]

    baseline_map = {r.get("search_term", ""): r for r in (baseline_rows or [])}

    rows: list[dict[str, str]] = []
    for kw in keywords:
        base = baseline_map.get(kw, {})
        prev = existing.get(kw, {})
        rows.append({
            "week": week,
            "search_term": kw,
            "lightfern_mentioned": base.get("lightfern_mentioned", prev.get("lightfern_mentioned", "pending")),
            "top_competitors": base.get("top_competitors", prev.get("top_competitors", "")),
            "visibility_notes": base.get("visibility_notes", prev.get("visibility_notes", "Scaile tracking from setup date")),
            "content_piece": base.get("content_piece", prev.get("content_piece", "")),
            "action": base.get("action", prev.get("action", "Monitor in Scaile dashboard")),
            "scaile_api_status": base.get("scaile_api_status", "dashboard_only"),
        })

    with tracking_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run_scaile_sync(config_path: Path | None = None) -> dict[str, Any]:
    _load_env()
    root = Path(__file__).resolve().parents[1]
    cfg_path = config_path or root / "config" / "pipeline.yaml"

    keywords = [
        "AI email writing tool",
        "best AI email tools to preserve your writing voice",
        "AI writing for founders",
        "best AI email tools to avoid generic AI writing",
        "best email autocomplete",
    ]
    tracking = root / "inbound" / "scaile_tracking.csv"

    if cfg_path.exists() and __import__("yaml"):
        import yaml
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        keywords = cfg.get("scaile", {}).get("keywords", keywords)
        tracking = root / cfg.get("scaile", {}).get("tracking_csv", "inbound/scaile_tracking.csv")

    api_ok, api_result = try_api_get("/v1/trackers")
    sync_tracking_csv(tracking, keywords)

    return {
        "keywords": len(keywords),
        "tracking_csv": str(tracking),
        "api_reachable": api_ok,
        "api_detail": api_result if not api_ok else "connected",
        "note": "Scaile scores accumulate from keyword setup date; see inbound/scaile_baseline.md for day-0 snapshot.",
    }


def main() -> int:
    result = run_scaile_sync()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
