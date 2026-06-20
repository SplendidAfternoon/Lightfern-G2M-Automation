"""Zero CRM API — push scored champion contacts."""

from __future__ import annotations

import csv
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_BASE = "https://api.zero.inc"


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
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def list_contacts(limit: int = 100) -> list[dict[str, Any]]:
    _load_env()
    key = os.environ.get("ZERO_API_KEY", "")
    ws = os.environ.get("ZERO_WORKSPACE_ID", "")
    if not key or not ws:
        return []
    url = f"{DEFAULT_BASE}/api/contacts?workspaceId={ws}&limit={limit}"
    req = urllib.request.Request(url, headers=_headers(key))
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("data", [])


def _normalize_linkedin(url: str) -> str:
    u = (url or "").strip().lower().rstrip("/")
    u = u.replace("https://www.", "https://").replace("http://www.", "http://")
    return u


def _existing_contact_keys() -> tuple[set[str], set[str]]:
    linkedin_keys: set[str] = set()
    name_keys: set[str] = set()
    for c in list_contacts(limit=200):
        if c.get("source") == "lightfern_champion_scorer":
            li = _normalize_linkedin(c.get("linkedin") or "")
            if li:
                linkedin_keys.add(li)
            name = (c.get("name") or "").strip().lower()
            if name:
                name_keys.add(name)
    return linkedin_keys, name_keys


def create_contact(payload: dict[str, Any], api_key: str | None = None) -> dict[str, Any]:
    _load_env()
    key = api_key or os.environ.get("ZERO_API_KEY", "")
    if not key:
        raise ValueError("ZERO_API_KEY not set")

    workspace_id = os.environ.get("ZERO_WORKSPACE_ID", "")
    if workspace_id and "workspaceId" not in payload:
        payload = {**payload, "workspaceId": workspace_id}

    url = f"{DEFAULT_BASE.rstrip('/')}/api/contacts"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=_headers(key), method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def contact_from_scored_row(row: dict[str, str]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": row.get("name", ""),
        "email": row.get("email") or None,
        "title": row.get("role", ""),
        "linkedin": row.get("linkedin") or None,
        "source": "lightfern_champion_scorer",
        "externalId": (row.get("linkedin") or row.get("email") or row.get("name", "")).strip(),
        "type": row.get("tier", "lead"),
        "custom": {
            "champion_score": row.get("champion_score", ""),
            "strongest_signal": row.get("strongest_signal", ""),
            "outreach_angle": row.get("outreach_angle", ""),
            "pipeline_stage": row.get("pipeline_stage", "Identified"),
            "tier": row.get("tier", ""),
        },
    }
    return {k: v for k, v in payload.items() if v is not None and v != ""}


def push_csv(
    csv_path: Path,
    tiers: list[str] | None = None,
    dry_run: bool = False,
    skip_existing: bool = True,
) -> tuple[int, int, int]:
    """
    Push scored contacts to Zero.
    Returns (created, skipped, failed).
    Default tiers: Tier A + Tier B (not Reject).
    """
    _load_env()
    key = os.environ.get("ZERO_API_KEY", "")
    if not key and not dry_run:
        raise ValueError("ZERO_API_KEY not set — use --dry-run to preview")

    if tiers is None:
        tiers = ["Tier A", "Tier B"]

    existing, existing_names = _existing_contact_keys() if skip_existing and not dry_run else (set(), set())
    created, skipped, failed = 0, 0, 0

    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            tier = row.get("tier", "")
            if tier not in tiers:
                continue
            li = _normalize_linkedin(row.get("linkedin") or "")
            name_key = (row.get("name") or "").strip().lower()
            if skip_existing and ((li and li in existing) or (name_key and name_key in existing_names)):
                skipped += 1
                continue
            payload = contact_from_scored_row(row)
            if dry_run:
                print(json.dumps(payload, indent=2))
                created += 1
                continue
            try:
                create_contact(payload)
                created += 1
                if li:
                    existing.add(li)
                if name_key:
                    existing_names.add(name_key)
            except urllib.error.HTTPError as e:
                body = e.read().decode(errors="replace")
                if e.code == 409 or "duplicate" in body.lower():
                    skipped += 1
                else:
                    print(f"Failed {row.get('name')}: {e.code} {body[:200]}", file=__import__("sys").stderr)
                    failed += 1
    return created, skipped, failed


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Push scored contacts to Zero CRM")
    parser.add_argument("--csv", default="output/scored_leaderboard.csv")
    parser.add_argument("--tier", default="A,B", help="Comma tiers e.g. A,B or all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    csv_path = root / args.csv
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
