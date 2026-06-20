# Lightfern Champion GTM System — Submission Deck

Use this as slide copy. Add screenshots from Unify, `python run_pipeline.py` output, Zero CRM, Scaile, and Unify email templates.

---

## Tech stack (for CS judges)

| Layer | Tool | What it does | How we use it |
|---|---|---|---|
| **Orchestration** | Python 3 + `run_pipeline.py` | Chains the full pipeline in one command | `python run_pipeline.py` |
| **Config** | YAML (`config/signals.yaml`, `config/pipeline.yaml`) | Scoring rules + pipeline settings without code changes | Edit keywords, tiers, paths |
| **Data in** | UnifyGTM Data API + Bulk API + CSV exports | Pull person records from Unify | API connected; audience CSVs in `data/` are live source |
| **Intelligence** | `score_prospects.py` (Cursor build) | Scores 0–100, tags strongest signal, writes outreach angle | Custom hackathon deliverable |
| **CRM** | Zero CRM REST API | Store scored contacts with champion metadata | Bearer auth; `custom.champion_score` on each contact |
| **Outbound send** | UnifyGTM Sequences | Email sequences to Tier A | Import `output/tier_a_unify_export.csv` — we do not push back to Unify via API |
| **Inbound measure** | Scaile dashboard + `scaile_client.py` | Track AI search terms over time | Day-0 baseline via Perplexity; Scaile tracks forward from setup date |
| **Secrets** | `.env` | API keys (gitignored) | Unify, Zero, Scaile keys |

**Data flow:**

```
Unify audience CSV exports ──┐
Unify Data API (0 records) ├──► data/unify_contacts.csv + data/*edge*.csv
                             │
                             ▼
                 score_prospects.py (Champion Scorer)
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
      output/scored_leaderboard.csv   tier_a_unify_export.csv
                 │                       │
                 ▼                       ▼
           Zero CRM API            Unify Sequences (manual import)
                 │
                 ▼
      outreach/personalized_sequences.md

Scaile dashboard (5 keywords) ◄── inbound/scaile_tracking.csv
Perplexity baseline (day 0)   ◄── inbound/scaile_baseline.md
```

**Honest limits:**
- Unify Data API person object is empty — audience lives in CSV exports until synced
- Scaile public API endpoint not reachable from our environment — dashboard + CSV sync used
- Signal detection uses CSV keywords + manual LinkedIn verification, not live social APIs

---

## Slide 1 — Challenge

**Lightfern needs champions, not just users.**

- AI email tool for high-stakes communication — founders, GTM leaders, VCs
- Product sits behind the scenes; growth depends on word-of-mouth from respected operators
- Raw contact lists aren't enough — we need **mission-aligned champions** with network effect

---

## Slide 2 — Signal Framework

**What makes a champion?**

| Signal | Weight |
|---|---|
| Substack / newsletter / blog | +20–25 |
| Writing craft / anti-AI-slop discourse | +15–20 |
| VC / accelerator / large audience | +10–20 |
| Founder / high email volume role | +15 |
| AI stack builder | +5–10 |

**Disqualify:** AI humanizers, cold-email automation, generic chatbot vendors

**Tiers:** Tier A (70+) → personalized outreach | Tier B (45–69) → lighter sequence | Reject (<45)

*Screenshot: scoring rubric table above*

---

## Slide 3 — Unify Pipeline

**Outbound engine: founder-led AI buyers**

- Unify audience configured for Founder/CEO, AI-native companies, US/UK
- Latest batch: **"Founders with edge and public voice"** (10 contacts) merged into pipeline
- Contacts pulled via Unify API (connected) + audience CSV exports in `data/`
- Tier A exported to `output/tier_a_unify_export.csv` for Unify **sequence import**

*Screenshot: Unify audience list showing "Founders with edge and public voice"*

*Screenshot: Unify CSV export or import screen*

---

## Slide 4 — Champion Scoring (Cursor)

**Custom intelligence layer**

```text
python run_pipeline.py
→ 48 contacts scored (17 Tier A, 23 Tier B, 8 Reject)
→ Each tagged with strongest signal + outreach angle
→ Pushed to Zero CRM with champion_score in custom fields
```

**Where to find scored contacts:**
- **File:** `output/scored_leaderboard.csv` (all contacts, ranked)
- **Zero CRM:** filter source = `lightfern_champion_scorer`
- **Tier A only:** `output/tier_a_unify_export.csv`

*Screenshot: terminal output from `python run_pipeline.py`*

*Screenshot: `output/scored_leaderboard.csv` open in Excel/Sheets*

**Top Tier A (examples):**

| Name | Score | Strongest signal |
|---|---|---|
| Ana Chubinidze | 100 | Substack author |
| Jacob Colker | 100 | VC / Accelerator |
| Emma Fieldhouse | 100 | Public writing |

---

## Slide 5 — Zero + Scaile

**Zero CRM (outbound tracking)**
- Tier A + Tier B champions pushed via Zero REST API
- Custom fields: `champion_score`, `strongest_signal`, `outreach_angle`, `tier`
- Pipeline stages: Identified → Enriched → Sequenced → Contacted → Engaged → Champion

**Zero automation & agents**
- REST API push from `run_pipeline.py` — no manual CSV import to Zero
- Contacts tagged `source=lightfern_champion_scorer` for filtering and future agent workflows
- Next step: Zero agents auto-advance stage when Unify sequence replies land (not wired in hackathon scope)

**Inbound (Scaile + Perplexity baseline, 2026-06-20)**
- Day-0 snapshot: Perplexity product-intent queries (`inbound/scaile_baseline.md`)
- Lightfern not cited in generic email tool queries (WriteMail, QuillBot, Superhuman dominate)
- Forward tracking: 5 keywords in Scaile dashboard (scores accumulate from setup date)
- 3 content pieces mapped to gaps (`inbound/inbound_pipeline.md`)

*Screenshot: Zero CRM — contacts filtered by source, custom fields visible*

*Screenshot: Scaile dashboard — 5 tracked keywords*

---

## Slide 6 — Outreach

**Personalised approach — no template smell**

Each email references the contact's **strongest signal**:

- **Jacob Colker (VC/accelerator):** "The emails your founders send before Demo Day"
- **Ana Chubinidze (Substack):** Reference governance newsletter + opinionated voice
- **Emma Fieldhouse (public writing):** "Blogging at Ramp — and email that matches"

**3-touch sequence:**
1. Signal-led opener (no product pitch in subject)
2. Mission bridge (human voice vs AI slop)
3. Low-friction ask (free access + optional referral for Tier A)

*Screenshot: Unify sequence editor — Touch 1 email for Jacob Colker (subject + body visible)*

*Screenshot: Unify sequence editor — Touch 1 email for Ana Chubinidze or Emma Fieldhouse*

*Screenshot: `outreach/personalized_sequences.md` — full 3-touch copy for reference*

---

## Close

> "Unify finds them, our scorer ranks them, Zero tracks them, Unify sequences reach out, Scaile measures if they can find us back."

Runs on 1–2 people. One command: `python run_pipeline.py`

**Your screenshot checklist:**
- [ ] Unify audience ("Founders with edge and public voice")
- [ ] Pipeline terminal output
- [ ] Zero CRM contacts with custom fields
- [ ] Scaile dashboard (5 keywords)
- [ ] Unify email template — Touch 1 (2 contacts)
- [ ] Optional: scored CSV / leaderboard

**Video recording:** see `deck/VIDEO_SCRIPT.md` — 2–3 min talk track + screen cues for Cursor demo.
