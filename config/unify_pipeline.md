# Unify Pipeline — Founder-Led AI Buyers

Configure this audience in UnifyGTM before or alongside the Champion Scorer.

## Audience filters

| Filter | Value |
|---|---|
| Title | Founder, Co-Founder, CEO, Managing Director |
| Company keywords | AI, artificial intelligence, machine learning, generative |
| Geography | US ~80%, UK ~20% |
| Seniority | C-suite, Founder |

## Signals to enable in Unify

- Founder / CEO role
- AI-native company (domain or description contains AI)
- High email volume role (founder, GTM, partnerships)

## Export fields (API or CSV)

Required for `score_prospects.py`:

- `name` (or Person)
- `company` (or Company)
- `role` (or Title)
- `linkedin` (or LinkedIn URL)
- `email` (or Work Email)
- `notes` (optional — enrichment rationale)
- `country` (optional)

## API pull

```bash
# Set UNIFY_API_KEY in .env, then:
python -m integrations.unify_client --export data/unify_contacts.csv
```

Uses Unify Data API: `GET https://api.unifygtm.com/data/v1/objects/{object}/records`

Person records are merged with local CSVs in `score_prospects.py`.

## Sequence setup (post-scoring)

1. Import Tier A from `output/zero_import.csv` into Zero CRM
2. Load Tier A emails into Unify sequence "Lightfern Champions — Tier A"
3. Use `outreach_angle` column as merge field / first-line personalization
