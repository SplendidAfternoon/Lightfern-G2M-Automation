# Lightfern Champion GTM System

Hackathon submission: find champions, reach them personally, make Lightfern discoverable.

## One command

```powershell
cd Desktop\lightfern-gtm-hackathon
pip install -r requirements.txt
copy .env.example .env   # add API keys

python run_pipeline.py
```

## Pipeline chain

```
[1] Unify pull     integrations/unify_client.py  -> data/unify_contacts.csv
[2] Score         score_prospects.py             -> output/scored_leaderboard.csv
[3] Zero push     integrations/zero_client.py    -> Zero CRM (Tier A + B)
[4] Scaile sync   integrations/scaile_client.py  -> inbound/scaile_tracking.csv
```

**We pull FROM Unify, not push TO Unify.** Tier A CSV goes into Unify sequences manually for outbound email.

## Where are my contacts?

| Location | What's there |
|---|---|
| `output/scored_leaderboard.csv` | All **48** scored contacts, ranked |
| `output/tier_a_unify_export.csv` | **17** Tier A — import to Unify sequences |
| `output/zero_import.csv` | **40** Tier A + B for CRM |
| **Zero CRM** | Filter source = `lightfern_champion_scorer` |
| **Unify** | Import tier_a CSV into a sequence (outbound send) |

## Tech stack

See **deck/SUBMISSION_DECK.md** — Tech stack section.

## API keys (.env)

Copy `.env.example` to `.env` and add your own keys locally. **Never commit `.env`** — it is gitignored.

```powershell
copy .env.example .env
```

- `UNIFY_API_KEY` — pull audience (Data API + Bulk API)
- `ZERO_API_KEY` + `ZERO_WORKSPACE_ID` — push scored contacts
- `SCAILE_API_KEY` — tracking sync (dashboard is primary; API may be app-only)

## Submission deck

`deck/SUBMISSION_DECK.md`
