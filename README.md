# 🚀 Lightfern Champion GTM System

> A Go-To-Market automation pipeline built to identify, score, and reach top champions.

This project was built as a hackathon submission. It is an automated data pipeline designed to pull prospect lists, algorithmically score them to find high-value "Champions," and seamlessly route them into outbound sequencing and CRM tools.

## 🔄 How it Works (The Pipeline)

The system operates in a 4-step automated chain:
1. **Pull (Unify):** Extracts raw prospect data from Unify.
2. **Score (Algorithm):** Evaluates prospects and generates a ranked leaderboard.
3. **Route (Zero CRM):** Automatically pushes Tier A and Tier B prospects into Zero CRM.
4. **Sync (Scaile):** Updates Scaile tracking for inbound discovery.

*Note: Tier A prospects are isolated into a specific export for manual injection into Unify's outbound email sequences.*

## 📂 Data Outputs

Running the pipeline generates clean, tiered CSVs ready for action:

| Export | Description |
|---|---|
| `scored_leaderboard.csv` | The master list of all scored and ranked contacts. |
| `tier_a_unify_export.csv` | Top-tier prospects ready for immediate outbound sequencing. |
| `zero_import.csv` | Cleaned data for CRM ingestion (Tier A + B). |

## 🛠️ Quick Start

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/SplendidAfternoon/lightfern-gtm-hackathon.git
   cd lightfern-gtm-hackathon
   pip install -r requirements.txt
   ```

2. Set up your environment variables (requires Unify, Zero, and Scaile API keys):
   ```bash
   cp .env.example .env
   ```

3. Run the end-to-end pipeline:
   ```bash
   python run_pipeline.py
   ```

## 📖 Learn More
Check out the full submission details and technical architecture in `deck/SUBMISSION_DECK.md`.