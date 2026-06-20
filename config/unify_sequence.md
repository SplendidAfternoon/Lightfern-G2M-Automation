## UnifyGTM Tier A sequence config

**Audience source:** `output/tier_a_unify_export.csv`  
**Sequence name:** Lightfern Champions - Tier A  
**Merge fields:** name, company, outreach_angle, strongest_signal

### Import steps

1. Export Tier A: `output/tier_a_unify_export.csv` (8 contacts)
2. In UnifyGTM, create sequence with 3 steps (Day 0, 4, 8)
3. Use `outreach_angle` as personalization hook in step 1 body
4. Reference `outreach/personalized_sequences.md` for full examples

### Step templates (use merge fields)

**Step 1 subject:** `{{strongest_signal}} - quick note`  
**Step 1 body opener:** `{{outreach_angle}}`

**Step 2 subject:** Quality over automation  
**Step 3 subject:** Free access + feedback

### API push (optional)

```powershell
python -m integrations.unify_client --export data/unify_contacts.csv
python score_prospects.py
# Upload tier_a_unify_export.csv via Unify UI or Data API upsert
```
