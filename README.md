# 🚀 Lightfern Champion GTM System

> A Go-To-Market automation pipeline built to identify, score, and reach top champions.

**Note:** This is an archived technical reference for a data pipeline built during a hackathon. The original setup required proprietary API keys for Zero CRM and Unify which have been rotated. 

This project is an automated data pipeline designed to pull prospect lists, algorithmically score them to find high-value "Champions," and seamlessly route them into outbound sequencing and CRM tools.

## 🔄 How it Works (The Pipeline)

The system operates in a 4-step automated chain:
1. **Pull (Unify):** Extracts raw prospect data from Unify via bulk API endpoints.
2. **Score (Algorithm):** Evaluates prospects and generates a ranked leaderboard based on algorithmic scoring criteria.
3. **Route (Zero CRM):** Automatically pushes Tier A and Tier B prospects into Zero CRM.
4. **Sync (Scaile):** Updates Scaile tracking for inbound discovery.

*Note: Tier A prospects were historically isolated into a specific export for manual injection into Unify's outbound email sequences.*

## 📂 Data Outputs

Running the pipeline generated clean, tiered CSV structures ready for action:

| Export | Description |
|---|---|
| `scored_leaderboard.csv` | The master list of all scored and ranked contacts. |
| `tier_a_unify_export.csv` | Top-tier prospects ready for immediate outbound sequencing. |
| `zero_import.csv` | Cleaned data for CRM ingestion (Tier A + B). |

## 📖 Technical Details
For deeper insights into the pipeline design, refer to the original architectural breakdown in `deck/SUBMISSION_DECK.md`.