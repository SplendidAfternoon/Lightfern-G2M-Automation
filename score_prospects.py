#!/usr/bin/env python3
"""
Lightfern Champion Scorer — scores contacts 0-100 and generates outreach angles.

Usage:
  python score_prospects.py
  python score_prospects.py --data-dir data --output-dir output
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


@dataclass
class SignalHit:
    category: str
    label: str
    points: int


@dataclass
class ScoredContact:
    name: str
    company: str
    role: str
    linkedin: str
    email: str
    country: str
    notes: str
    source_csv: str
    hits: list[SignalHit] = field(default_factory=list)
    penalties: list[str] = field(default_factory=list)
    manual_bonus: int = 0

    @property
    def raw_score(self) -> int:
        return sum(h.points for h in self.hits) + self.manual_bonus

    @property
    def champion_score(self) -> int:
        penalty = min(30, len(self.penalties) * 15)
        return max(0, min(100, self.raw_score - penalty))

    @property
    def disqualified(self) -> bool:
        return bool(self.penalties) and self.raw_score < 50

    @property
    def tier(self) -> str:
        if self.disqualified or self.champion_score < 45:
            return "Reject"
        if self.champion_score >= 70:
            return "Tier A"
        return "Tier B"

    @property
    def strongest_signal(self) -> str:
        if not self.hits:
            return "Founder-led AI buyer"
        # Prefer specific signals over composite/generic
        ranked = sorted(
            [h for h in self.hits if h.category not in ("composite", "ai_native_company")],
            key=lambda h: h.points,
            reverse=True,
        )
        if ranked:
            return ranked[0].label
        return self.hits[0].label

    def outreach_angle(self, angles: dict[str, str]) -> str:
        label = self.strongest_signal.lower()
        if "substack" in label or "newsletter" in label or "blog" in label:
            return angles.get("substack_author", angles["default"]).replace(
                "their newsletter", f"your work at {self.company or 'your company'}"
            )
        if "accelerator" in label or "vc" in label or "investor" in label or "incubator" in label:
            return angles.get("vc_accelerator", angles["default"])
        if "writing" in label or "craft" in label or "communication" in label:
            return angles.get("writing_craft", angles["default"])
        if "stack" in label or "tool" in label:
            return angles.get("stack_builder", angles["default"])
        if "gtm" in label or "partnership" in label:
            return angles.get("gtm_leader", angles["default"])
        if "founder" in label or "ceo" in label:
            return angles.get("founder_ceo", angles["default"])
        return angles["default"].replace("their", f"{self.name.split()[0]}'s" if self.name else "their")


def load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise SystemExit("Install PyYAML: pip install pyyaml")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_text(*parts: str) -> str:
    return " ".join(p.lower() for p in parts if p)


def normalize_linkedin(url: str) -> str:
    u = (url or "").strip().lower().rstrip("/")
    return u.replace("https://www.", "https://").replace("http://www.", "http://")


def contact_key(contact: ScoredContact) -> str:
    li = normalize_linkedin(contact.linkedin)
    if li:
        return li
    email = (contact.email or "").strip().lower()
    if email:
        return email
    return contact.name.strip().lower()


def match_keywords(text: str, keywords: list[str]) -> bool:
    return any(kw in text for kw in keywords)


def load_manual_signals(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            key = row.get("name", "").strip().lower()
            if key:
                out[key] = row
    return out


def parse_csv_row(row: dict[str, str], source: str) -> ScoredContact | None:
    # Normalize BOM-prefixed keys from Excel exports
    row = {k.lstrip("\ufeff"): v for k, v in row.items()}
    name = (row.get("name") or row.get("Person") or row.get("Founder") or "").strip()
    if not name:
        return None
    note_parts = [
        row.get("notes") or row.get("Rationale") or row.get("Coverage") or "",
        row.get("Why They Have Edge") or "",
        row.get("Public Channels") or "",
    ]
    notes = "; ".join(p.strip() for p in note_parts if p and p.strip())
    return ScoredContact(
        name=name,
        company=(row.get("company") or row.get("Company") or "").strip(),
        role=(row.get("role") or row.get("Title") or "").strip(),
        linkedin=(row.get("linkedin") or row.get("LinkedIn URL") or "").strip(),
        email=(row.get("email") or row.get("Work Email") or "").strip(),
        country=(row.get("country") or row.get("Country") or "").strip(),
        notes=notes,
        source_csv=source,
    )


def load_contacts(data_dir: Path) -> list[ScoredContact]:
    contacts: dict[str, ScoredContact] = {}
    name_index: dict[str, str] = {}
    skip = {"manual_signals.csv"}

    csv_files = sorted(data_dir.glob("*.csv"))
    csv_files.sort(key=lambda p: (0 if p.name == "unify_contacts.csv" else 1, p.name))

    for path in csv_files:
        if path.name in skip:
            continue
        with path.open(newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                c = parse_csv_row(row, path.name)
                if not c:
                    continue
                key = contact_key(c)
                name_key = c.name.strip().lower()
                if name_key in name_index:
                    key = name_index[name_key]
                elif key in contacts:
                    name_index[name_key] = key
                else:
                    name_index[name_key] = key

                if key in contacts:
                    existing = contacts[key]
                    if not existing.email and c.email:
                        existing.email = c.email
                    if not existing.linkedin and c.linkedin:
                        existing.linkedin = c.linkedin
                    if c.notes:
                        existing.notes = (
                            f"{existing.notes}; {c.notes}".strip("; ")
                            if existing.notes
                            else c.notes
                        )
                    if "edge" in path.name.lower() or c.source_csv.startswith("unify"):
                        existing.source_csv = c.source_csv
                else:
                    contacts[key] = c
    return list(contacts.values())


def apply_signals(contact: ScoredContact, config: dict[str, Any], manual: dict[str, dict[str, Any]]) -> None:
    text = normalize_text(contact.name, contact.role, contact.company, contact.notes, contact.linkedin)

    for neg in config.get("negative_disqualify", []):
        if neg in text:
            contact.penalties.append(neg)

    categories = [
        ("role_founder_ceo", "Founder / CEO"),
        ("role_vc_accelerator", "VC / Accelerator"),
        ("role_gtm_partnerships", "GTM / Partnerships"),
        ("public_writing", "Public writing (newsletter/blog)"),
        ("writing_craft", "Writing craft discourse"),
        ("stack_builder", "AI stack builder"),
        ("network_community", "Community / thought leader"),
        ("ai_native_company", "AI-native company"),
    ]

    for key, label in categories:
        block = config.get(key, {})
        kws = block.get("keywords", [])
        pts = block.get("points", 0)
        if kws and match_keywords(text, kws):
            contact.hits.append(SignalHit(key, label, pts))

    # Composite: founder-led AI buyer (core ICP)
    has_founder = any(h.category == "role_founder_ceo" for h in contact.hits)
    has_ai = any(h.category == "ai_native_company" for h in contact.hits)
    if has_founder and has_ai:
        contact.hits.append(SignalHit("composite", "Founder-led AI buyer", 35))

    # Verified contact bonus
    if "verified" in text:
        contact.hits.append(SignalHit("composite", "Verified contact", 5))

    role_hits = [h for h in contact.hits if h.category.startswith("role_")]
    if len(role_hits) > 1:
        best = max(role_hits, key=lambda h: h.points)
        contact.hits = [h for h in contact.hits if not h.category.startswith("role_")] + [best]

    manual_row = manual.get(contact.name.lower())
    if manual_row:
        bonus = 0
        if manual_row.get("has_substack", "").lower() == "true":
            contact.hits.append(SignalHit("manual", "Substack author", 25))
            bonus += 5
        if manual_row.get("has_newsletter", "").lower() == "true":
            contact.hits.append(SignalHit("manual", "Newsletter author", 22))
            bonus += 3
        if manual_row.get("large_audience", "").lower() == "true":
            contact.hits.append(SignalHit("manual", "Large engaged audience", 15))
            bonus += 5
        if manual_row.get("vc_accelerator", "").lower() == "true":
            contact.hits.append(SignalHit("manual", "VC / Accelerator operator", 20))
            bonus += 5
        if manual_row.get("writing_craft_posts", "").lower() == "true":
            contact.hits.append(SignalHit("manual", "Writing craft posts", 18))
            bonus += 3
        extra = manual_row.get("notes", "")
        if extra:
            contact.notes = f"{contact.notes}; {extra}".strip("; ")
        contact.manual_bonus = bonus


def score_all(contacts: list[ScoredContact], config: dict[str, Any], manual: dict[str, dict[str, Any]]) -> list[ScoredContact]:
    for c in contacts:
        apply_signals(c, config, manual)
    return sorted(contacts, key=lambda c: c.champion_score, reverse=True)


def to_row(contact: ScoredContact, angles: dict[str, str]) -> dict[str, str]:
    return {
        "name": contact.name,
        "company": contact.company,
        "role": contact.role,
        "linkedin": contact.linkedin,
        "email": contact.email,
        "country": contact.country,
        "champion_score": str(contact.champion_score),
        "tier": contact.tier,
        "strongest_signal": contact.strongest_signal,
        "outreach_angle": contact.outreach_angle(angles),
        "signal_breakdown": "; ".join(f"{h.label} (+{h.points})" for h in contact.hits),
        "penalties": "; ".join(contact.penalties),
        "source_csv": contact.source_csv,
        "pipeline_stage": "Identified",
    }


LEADERBOARD_FIELDS = [
    "name", "company", "role", "linkedin", "email", "country",
    "champion_score", "tier", "strongest_signal", "outreach_angle",
    "signal_breakdown", "penalties", "source_csv", "pipeline_stage",
]

ZERO_FIELDS = [
    "name", "email", "role", "linkedin", "company", "country",
    "champion_score", "tier", "strongest_signal", "outreach_angle", "pipeline_stage",
]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def print_leaderboard(scored: list[ScoredContact], angles: dict[str, str], limit: int = 15) -> None:
    print("\n" + "=" * 72)
    print("LIGHTFERN CHAMPION LEADERBOARD")
    print("=" * 72)
    tier_a = [c for c in scored if c.tier == "Tier A"]
    tier_b = [c for c in scored if c.tier == "Tier B"]
    rejected = [c for c in scored if c.tier == "Reject"]
    print(f"Total: {len(scored)} | Tier A: {len(tier_a)} | Tier B: {len(tier_b)} | Reject: {len(rejected)}")
    print("-" * 72)
    for i, c in enumerate(scored[:limit], 1):
        row = to_row(c, angles)
        print(f"{i:2}. [{row['tier']:6}] {row['champion_score']:>3}  {c.name[:28]:28}  {row['strongest_signal']}")
        print(f"     Angle: {row['outreach_angle'][:65]}")
    print("=" * 72 + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Score Lightfern champion prospects")
    parser.add_argument("--config", default="config/signals.yaml")
    parser.add_argument("--manual", default="config/manual_signals.csv")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--top", type=int, default=15, help="Rows to print")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    config = load_yaml(root / args.config)
    manual = load_manual_signals(root / args.manual)
    contacts = load_contacts(root / args.data_dir)

    if not contacts:
        print("No contacts found in data/")
        return 1

    angles = config.get("outreach_angles", {})
    scored = score_all(contacts, config, manual)
    rows = [to_row(c, angles) for c in scored]

    out_dir = root / args.output_dir
    write_csv(out_dir / "scored_leaderboard.csv", rows, LEADERBOARD_FIELDS)
    write_csv(
        out_dir / "zero_import.csv",
        [r for r in rows if r["tier"] in ("Tier A", "Tier B")],
        ZERO_FIELDS,
    )
    write_csv(
        out_dir / "tier_a_unify_export.csv",
        [r for r in rows if r["tier"] == "Tier A"],
        ZERO_FIELDS,
    )

    print_leaderboard(scored, angles, limit=args.top)
    print(f"Wrote {out_dir / 'scored_leaderboard.csv'}")
    print(f"Wrote {out_dir / 'zero_import.csv'}")
    print(f"Wrote {out_dir / 'tier_a_unify_export.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
