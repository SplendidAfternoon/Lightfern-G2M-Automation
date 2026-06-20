# Zero CRM Pipeline Stages

Import scored contacts from `output/zero_import.csv`.

## Stages

| Stage | Trigger |
|---|---|
| **Identified** | Contact appears in scored leaderboard (default on import) |
| **Enriched** | Public signals verified in `config/manual_signals.csv` |
| **Sequenced** | Added to UnifyGTM Tier A sequence |
| **Contacted** | First email sent from Unify |
| **Engaged** | Reply or link click |
| **Champion** | Active Lightfern user + willing to refer |

## Custom fields (stored on contact)

- `champion_score`
- `strongest_signal`
- `outreach_angle`
- `tier`
- `linkedin_url`

## Push via API

```powershell
# Preview payloads
python push_pipeline.py --dry-run

# Push Tier A only (default)
python push_pipeline.py

# Push all tiers
python push_pipeline.py --tier all
```

Requires `ZERO_API_KEY` and `ZERO_WORKSPACE_ID` in `.env`.

## Push via Zero MCP (live demo)

After import, use Zero MCP in Cursor to:
- List contacts tagged `source: lightfern_champion_scorer`
- Update stage to Enriched / Sequenced
- Add notes with outreach angle from CSV
