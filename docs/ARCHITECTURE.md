# Architecture – Sentiment Evolution Tracker

## Overview

Sentiment Evolution Tracker is a **Model Context Protocol (MCP)** server that augments Claude Desktop with persistent sentiment analytics and customer risk monitoring.

```
┌─────────────────────────────────────────────────────────────┐
│                       CLAUDE DESKTOP                        │
│                   (Conversational UI)                       │
└────────────────┬────────────────────────────────────────────┘
                 │ MCP Protocol (stdio)
┌────────────────▼────────────────────────────────────────────┐
│            MCP SERVER (src/mcp_server.py)                   │
│  ├─ analyze_customer                                        │
│  ├─ get_customer_profile                                    │
│  ├─ predict_risk                                            │
│  ├─ detect_patterns                                         │
│  ├─ generate_alerts                                         │
│  └─ export_data                                             │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┬──────────┬──────────┐
        │                 │          │          │
┌───────▼────────┐ ┌─────▼───┐ ┌──▼─────┐ ┌──▼─────┐
│ Sentiment      │ │ Pattern │ │ Risk   │ │Database│
│ Analyzer       │ │Detector │ │ Engine │ │Manager │
│ (TextBlob)     │ │         │ │        │ │        │
└────────────────┘ └─────────┘ └────────┘ └───┬────┘
                                               │
                                    ┌──────────▼────────────┐
                                    │  SQLite3 Database     │
                                    │  ├─ customer_profiles │
                                    │  ├─ conversations     │
                                    │  └─ risk_alerts       │
                                    └──────────────────────┘
```

## Core Components

### 1. `mcp_server.py`
- Entry point that runs the MCP stdio server.
- Registers seven tools and validates all payloads.
- Manages session context, structured logs, and error surfaces.

### 2. `sentiment_analyzer.py`
- Wraps TextBlob/NLTK to derive a normalized 0–100 sentiment score.
- Detects trend deltas against the historical baseline.

```
Input:  "Great support but pricing hurts"
  ↓ tokenization → polarity (-1..1) → normalization (0..100)
Output: 61/100 (slightly positive)
```

### 3. `pattern_detector.py`
- Flags directional changes using the historical sentiment sequence.
- Possible trends: `RISING`, `DECLINING`, `STABLE`.

### 4. `risk_predictor.py`
- Calculates churn probability based on trend strength, velocity, and latest sentiment.
- Produces a 0–1 score plus a qualitative risk bucket.

### 5. `database_manager.py`
- SQLite wrapper responsible for persistence and migrations.
- Tables:
  - `customer_profiles(customer_id, lifetime_sentiment, churn_risk, total_interactions, first_contact, last_contact, context_type)`
  - `conversations(id, customer_id, analysis_date, message_content, sentiment_score, sentiment_trend, risk_level)`
  - `risk_alerts(id, customer_id, severity, alert_date, resolved, description)`

---

## Data Flow

When Claude calls `analyze_customer`:

```
1. Claude sends request via MCP.
2. `mcp_server.py` validates schema and orchestrates modules.
3. `sentiment_analyzer.py` scores each message.
4. `pattern_detector.py` classifies the sentiment trend.
5. `risk_predictor.py` estimates churn probability and severity.
6. `database_manager.py` upserts conversation records and alerts.
7. Response payload returns to Claude with sentiment, trend, risk, and guidance.
```

---

## Tool Contracts

### `analyze_customer`
```
Input:
{
  "customer_id": "ACME_CORP_001",
  "messages": ["Service delays", "Pricing too high"]
}

Output:
{
  "customer_id": "ACME_CORP_001",
  "sentiment_score": 35.0,
  "trend": "DECLINING",
  "risk_level": "HIGH",
  "recommendation": "ESCALATE_SUPPORT"
}
```

### `get_customer_profile`
```
Input: {"customer_id": "ACME_CORP_001"}

Output includes aggregate sentiment, churn risk, interaction count, history array, and active alerts.
```

---

## Persistence

Database location: `data/sentiment_analysis.db`

Characteristics:
- Single-file SQLite with indexed foreign keys.
- ACID transactions to avoid data loss during simultaneous tool calls.
- Optional backups can be scripted via `tools/export_data.py`.

---

## Claude Integration Flow

```
1. Claude Desktop starts and reads `claude_desktop_config.json`.
2. Claude launches the MCP server process via stdio.
3. Tools become available in the Claude UI.
4. Every tool invocation persists results in SQLite.
5. Future sessions reuse historical data without reanalysis.
```

---

## Worked Example

Call:

```python
analyze_customer({
    "customer_id": "ACME_CORP_001",
    "messages": ["Great onboarding but pricing is painful"]
})
```

Result sequence:

```python
sentiment = 58.5        # TextBlob normalized
trend = "DECLINING"     # compared to historical baseline
risk = 0.65              # composite churn score

database_manager.save_interaction(...)

return {
    "sentiment": 58.5,
    "trend": "DECLINING",
    "risk": 0.65,
    "action": "CONTACT_CUSTOMER_OFFERING_DISCOUNT"
}
```

---

## Scalability Notes

- Optimized for hundreds of customers and thousands of interactions.
- Tight coupling minimized; new tools plug in via the MCP registry.
- SQLite keeps deployment lightweight while supporting indexed lookups.

---

**Version:** 1.0.0 · **Status:** Production-ready
