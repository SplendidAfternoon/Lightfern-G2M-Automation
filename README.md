# Lightfern GTM Automation Pipeline

> An automated Go-To-Market (GTM) ETL pipeline featuring algorithmic prospect scoring, data normalization, and distributed CRM orchestration.

**Note:** This is an archived technical reference. The architecture relies on rotated API keys and deprecated endpoints for Zero CRM and Unify. It is preserved as a blueprint for multi-node GTM data engineering.

## Pipeline Architecture

The system operates as a 4-stage automated Extract, Transform, Load (ETL) and routing chain designed to minimize manual data entry and optimize outbound sales latency:

### 1. Data Ingestion & Extraction (Pull Layer)
- **Bulk API Polling:** Interfaces with Unify's REST APIs to asynchronously extract raw, unstructured prospect data.
- **Data Normalization:** Sanitizes and maps disparate JSON payloads into a unified, strict schema suitable for algorithmic evaluation.

### 2. Algorithmic Scoring Heuristics
- **Weighted Evaluation:** Processes normalized prospect data through a custom heuristics engine, evaluating key identifiers against ideal-customer-profile (ICP) thresholds.
- **Tiered Leaderboard Generation:** Mutates the dataset into a strict, ranked hierarchy (Tier A/B/C), exporting a deterministic `scored_leaderboard.csv` artifact.

### 3. CRM Orchestration & Routing (Push Layer)
- **Automated Ingestion:** Establishes a secure pipeline to push high-value (Tier A/B) prospects directly into Zero CRM.
- **State Synchronization:** Ensures data integrity by mapping custom fields and appending tracking metadata (e.g., `source = lightfern_champion_scorer`).
- **Segregated Outbound Generation:** Isolates top-percentile leads (`tier_a_unify_export.csv`) for targeted, manual injection into high-touch outbound sequencing endpoints.

### 4. Telemetry & Tracking
- **Inbound Discovery Sync:** Interfaces with Scaile APIs to maintain stateful tracking data across the sales funnel, closing the loop between outbound engagement and inbound analytics.