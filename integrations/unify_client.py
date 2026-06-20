"""UnifyGTM — pull audience contacts into the champion pipeline.

Flow: Unify (audience / Data API / CSV export) -> data/unify_contacts.csv -> scorer
We do NOT push scored contacts back into Unify for outbound; sequences run in Unify separately.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

BASE_URL = "https://api.unifygtm.com"
DATA_BASE = f"{BASE_URL}/data/v1"

EXPORT_FIELDS = [
    "name", "company", "role", "linkedin", "email", "country", "notes", "source_csv",
]


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
    return {"X-Api-Key": api_key, "Accept": "application/json", "Content-Type": "application/json"}


def _request(method: str, path: str, api_key: str, body: dict | None = None) -> dict[str, Any]:
    url = f"{BASE_URL}{path}" if path.startswith("/") else path
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=_headers(api_key), method=method)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_person_records(api_key: str, limit: int = 500) -> list[dict[str, Any]]:
    """Standard Data API — often empty until Unify person object is populated."""
    object_name = os.environ.get("UNIFY_PERSON_OBJECT", "person")
    result = _request("GET", f"{DATA_BASE}/objects/{object_name}/records?limit={limit}", api_key)
    return result.get("data", result.get("records", []))


def bulk_export_person_records(api_key: str, timeout_s: int = 90) -> list[dict[str, Any]]:
    """Bulk API query job for person records (preview API)."""
    object_name = os.environ.get("UNIFY_PERSON_OBJECT", "person")
    job = _request(
        "POST",
        f"{DATA_BASE}/objects/{object_name}/query-jobs",
        api_key,
        body={"limit": 500},
    )
    job_id = job.get("data", {}).get("id") or job.get("id")
    if not job_id:
        return []

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        status_resp = _request(
            "GET", f"{DATA_BASE}/objects/{object_name}/query-jobs/{job_id}", api_key
        )
        status = (status_resp.get("data") or status_resp).get("status", "")
        if status in ("completed", "succeeded", "success"):
            results = _request(
                "GET",
                f"{DATA_BASE}/objects/{object_name}/query-jobs/{job_id}/results",
                api_key,
            )
            return results.get("data", results.get("records", []))
        if status in ("failed", "cancelled", "canceled"):
            return []
        time.sleep(2)
    return []


def _normalize_linkedin(url: str) -> str:
    u = (url or "").strip().lower().rstrip("/")
    return u.replace("https://www.", "https://").replace("http://www.", "http://")


def _contact_key(rec: dict[str, str]) -> str:
    li = _normalize_linkedin(rec.get("linkedin", ""))
    if li:
        return li
    email = (rec.get("email") or "").strip().lower()
    if email:
        return email
    return (rec.get("name") or "").strip().lower()


def merge_audience_csvs(data_dir: Path) -> list[dict[str, str]]:
    """Fallback: merge Unify audience CSV exports from data/ folder."""
    patterns = ("*prospects*.csv", "*edge*.csv", "*voice*.csv", "unify_contacts.csv")
    paths: list[Path] = []
    seen: set[str] = set()
    for pattern in patterns:
        for path in sorted(data_dir.glob(pattern)):
            if path.name not in seen:
                seen.add(path.name)
                paths.append(path)

    contacts: dict[str, dict[str, str]] = {}
    name_index: dict[str, str] = {}
    for path in paths:
        if path.name == "unify_contacts.csv":
            continue  # output file, not a source export
        with path.open(newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                row = {k.lstrip("\ufeff"): v for k, v in row.items()}
                name = (row.get("Person") or row.get("Founder") or row.get("name") or "").strip()
                if not name:
                    continue
                rec = normalize_record_from_csv_row(row, path.name)
                key = _contact_key(rec)
                name_key = rec["name"].strip().lower()
                if name_key in name_index:
                    key = name_index[name_key]
                else:
                    name_index[name_key] = key
                if key in contacts:
                    existing = contacts[key]
                    for field in ("email", "linkedin", "notes", "role", "company"):
                        if not existing.get(field) and rec.get(field):
                            existing[field] = rec[field]
                else:
                    contacts[key] = rec
    return list(contacts.values())


def normalize_record_from_csv_row(row: dict[str, str], source: str) -> dict[str, str]:
    note_parts = [
        row.get("Rationale") or row.get("Coverage") or row.get("notes") or "",
        row.get("Why They Have Edge") or "",
        row.get("Public Channels") or "",
    ]
    notes = "; ".join(p.strip() for p in note_parts if p and p.strip())
    return {
        "name": (row.get("Person") or row.get("Founder") or row.get("name") or "").strip(),
        "company": (row.get("Company") or row.get("company") or "").strip(),
        "role": (row.get("Title") or row.get("role") or "").strip(),
        "linkedin": (row.get("LinkedIn URL") or row.get("linkedin") or "").strip(),
        "email": (row.get("Work Email") or row.get("email") or "").strip(),
        "country": (row.get("Country") or row.get("country") or "").strip(),
        "notes": notes,
        "source_csv": f"unify_export:{source}",
    }


def normalize_api_record(record: dict[str, Any]) -> dict[str, str]:
    attrs = record.get("attributes", record)
    if isinstance(attrs, dict) and "attributes" in record:
        attrs = record["attributes"]

    def pick(*keys: str) -> str:
        for k in keys:
            v = attrs.get(k) if isinstance(attrs, dict) else None
            if v:
                return str(v).strip()
        return ""

    return {
        "name": pick("name", "full_name", "display_name"),
        "company": pick("company_name", "company", "organization"),
        "role": pick("title", "job_title", "role"),
        "linkedin": pick("linkedin_url", "linkedin", "linkedin_profile_url"),
        "email": pick("email", "work_email", "primary_email"),
        "country": pick("country", "country_code"),
        "notes": pick("notes", "description", "bio"),
        "source_csv": "unify_api",
    }


def pull_audience(output_path: Path, data_dir: Path | None = None) -> tuple[list[dict[str, str]], str]:
    """
    Pull contacts from Unify API; fall back to audience CSV exports in data/.
    Returns (contacts, source_description).
    """
    _load_env()
    api_key = os.environ.get("UNIFY_API_KEY", "")
    records: list[dict[str, str]] = []

    source = "unify_api_empty"
    if api_key:
        try:
            raw = list_person_records(api_key)
            if not raw:
                raw = bulk_export_person_records(api_key)
            if raw:
                records = [normalize_api_record(r) for r in raw if normalize_api_record(r).get("name")]
                source = f"unify_api ({len(records)} person records)"
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            source = f"unify_api_error: {e}"
    else:
        source = "no_unify_api_key"

    if not records and data_dir:
        records = merge_audience_csvs(data_dir)
        if records:
            source = f"unify_audience_csv_fallback ({len(records)} from data/ audience exports)"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPORT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    return records, source


def main() -> int:
    parser = argparse.ArgumentParser(description="Pull Unify audience into unify_contacts.csv")
    parser.add_argument("--export", default="data/unify_contacts.csv")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = root / args.export
    contacts, source = pull_audience(out, data_dir=root / "data")
    print(f"Unify pull: {len(contacts)} contacts via {source}")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
