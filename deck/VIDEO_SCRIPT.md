# Video script — Lightfern GTM hackathon

**Target length:** 2–3 minutes  
**Format:** You talk, screen shows. Read this loosely — sound like yourself.

**Before you hit record:** Open these tabs/files so you can flip fast:
1. Cursor — project folder `lightfern-gtm-hackathon`
2. `config/signals.yaml`
3. `score_prospects.py`
4. `run_pipeline.py`
5. Terminal (already in project folder)
6. `output/scored_leaderboard.csv`
7. `outreach/personalized_sequences.md`
8. Zero CRM (filtered by source)
9. Unify — audience + sequence (optional but strong)

---

## 0:00 — Hook (10 sec)

**SAY:**  
"Lightfern doesn't need more users — it needs champions. I built a GTM system that finds mission-aligned founders, scores them, tracks them in CRM, and personalizes outbound. Most of it was built with Cursor in a hackathon sprint."

**SHOW:** `deck/SUBMISSION_DECK.md` — Slide 1 challenge line, or just the project folder in Cursor sidebar.

---

## 0:10 — How I used Cursor (25 sec)

**SAY:**  
"I used Cursor like a technical co-founder. I described the problem in plain English — find champions, not cold-email bots — and Cursor helped me scaffold the whole repo: scorer, API integrations, config files, and the submission deck. I didn't start from a blank Python file. I iterated in chat — fix this API auth, merge this CSV, push to Zero — and Cursor wrote and rewired the code while I focused on GTM logic."

**SHOW:** Cursor chat panel (if you have history, scroll briefly) **OR** the file tree:
- `score_prospects.py` — "Cursor built this"
- `integrations/` — "API clients"
- `config/signals.yaml` — "rules without touching code"

**Juicy moment:** Click `config/signals.yaml` — point at Substack + disqualify keywords.

**SAY (one line):**  
"The scoring rubric lives in YAML. I tuned weights in chat — Cursor updated the file. No redeploy, just re-run."

---

## 0:35 — The custom bit: Champion Scorer (30 sec)

**SAY:**  
"The hackathon deliverable is this scorer. It reads our Unify audience, applies signal rules, scores zero to a hundred, picks the strongest signal, and writes an outreach angle for each person. Tier A goes to personalized sequences. Tier B goes to a lighter track. Rejects get filtered out."

**SHOW:** `score_prospects.py` — scroll to the leaderboard print / tier logic (don't read code aloud).

**THEN SHOW:** `output/scored_leaderboard.csv` — sort by score. Point at columns:
- `champion_score`
- `strongest_signal`
- `outreach_angle`

**SAY:**  
"Forty-eight contacts. Seventeen Tier A. Each row is a decision, not just a name."

---

## 1:05 — One command demo (25 sec)

**SAY:**  
"Everything chains in one command. Unify in, score, Zero out, Scaile sync."

**SHOW:** Terminal — type or paste:

```powershell
cd Desktop\lightfern-gtm-hackathon
python run_pipeline.py
```

Let it run. **Don't narrate every line** — just point when the leaderboard appears.

**SAY:**  
"Pull, score, push, sync. That's the system."

**Juicy moment:** Pause on `Tier A: 17 | Tier B: 23 | Reject: 8`.

---

## 1:30 — Outbound: Unify + personalized copy (25 sec)

**SAY:**  
"Unify finds the audience. We don't spray templates — each email hooks their strongest signal. Jacob at an accelerator gets Demo Day framing. Ana with a governance Substack gets voice and policy, not a product pitch in the subject line."

**SHOW:** `outreach/personalized_sequences.md` — Jacob Colker Touch 1 subject line.

**THEN SHOW:** Unify sequence editor — same kind of personalization (screenshot or live).

**SAY:**  
"Cursor helped draft these sequences from the scorer's outreach angles. I edited for tone — Lightfern cares about human voice, not AI slop."

---

## 1:55 — Zero + inbound (20 sec)

**SAY:**  
"Scored contacts land in Zero via API — champion score, tier, outreach angle in custom fields. Filter by source `lightfern_champion_scorer`. For inbound, Scaile tracks five AI search terms; we documented a day-zero Perplexity baseline because Lightfern isn't visible yet — that's the gap we're closing with content."

**SHOW:** Zero CRM — contacts with custom fields visible.

**OPTIONAL SHOW:** Scaile dashboard — 5 keywords.

---

## 2:15 — Close (15 sec)

**SAY:**  
"Unify finds them, our scorer ranks them, Zero tracks them, Unify sequences reach out, Scaile measures if they can find us back. Built with Cursor, runs on one person, one command. Thanks."

**SHOW:** `run_pipeline.py` or the deck close quote:

> "Unify finds them, our scorer ranks them, Zero tracks them, Unify sequences reach out, Scaile measures if they can find us back."

---

## If you have extra time (+30 sec)

Pick **one** of these — don't cram all three:

| Extra | SHOW | SAY |
|---|---|---|
| **New Unify batch** | `data/Founders with edge and public voice.csv` | "I generated ten founders with public voice in Unify, exported, Cursor merged them into the pipeline — eight net-new champions." |
| **Honest limits** | `deck/SUBMISSION_DECK.md` honest limits | "Unify's person API is empty so we use CSV exports. Scaile API wasn't reachable — dashboard + baseline doc. We documented what works and what doesn't." |
| **Cursor iteration** | Chat or git history | "When Zero only showed ten contacts, I described the bug in Cursor — turned out we only pushed Tier A first. Fixed dedup and LinkedIn normalization in one session." |

---

## Cursor talking points (if they ask in comments / Q&A)

Short answers you can reuse:

- **"Did Cursor write everything?"** — "Cursor scaffolded and iterated. I owned the GTM strategy — signal framework, tiers, outreach angles, what counts as a champion."
- **"Why Cursor vs ChatGPT?"** — "Cursor edits the actual repo — files, terminal, API fixes — not copy-paste into random folders."
- **"Hardest part?"** — "Wiring real APIs with honest fallbacks when Unify's data API was empty and Scaile's endpoint didn't resolve."
- **"What would you build next?"** — "Zero agents that advance pipeline stage when Unify gets a reply, and inbound content to move Scaile scores."

---

## Recording tips

1. **Zoom browser to 125%** — judges on phones can read it.
2. **Hide `.env`** — never scroll past API keys.
3. **Pre-run** `python run_pipeline.py` once so the live run is fast and you know what you'll see.
4. **One take is fine** — hackathon videos don't need Hollywood edits.
5. **Speak slower than you think** — 2 minutes of script = ~250 words max.

---

## Ultra-short version (60 sec emergency cut)

1. Problem: champions not users (5 sec)
2. Cursor built scorer + pipeline in this repo (10 sec)
3. Run `python run_pipeline.py` — show leaderboard (15 sec)
4. Show CSV or Zero with scores + one personalized email (15 sec)
5. Close line + Scaile/Zero flash (15 sec)
