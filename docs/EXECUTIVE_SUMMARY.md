# Executive Summary – Sentiment Evolution Tracker

## Project Overview

Sentiment Evolution Tracker is a custom **Model Context Protocol (MCP)** server that lets Claude Desktop perform persistent sentiment analysis with database-backed memory.

## Motivation

Claude excels at single-turn analysis but cannot remember prior conversations. To unlock richer customer intelligence, we needed tooling that could:
1. Analyze customer conversations on demand.
2. Persist every result in a structured database.
3. Run historical queries across the full portfolio.
4. Surface churn risk patterns automatically.

## Solution

### Architecture

- **MCP server** (`src/mcp_server.py`) orchestrates requests coming from Claude.
- **Analysis modules** handle sentiment scoring, pattern detection, and risk prediction.
- **SQLite database** stores customer profiles, conversation history, and alerts.
- **Seven exposed tools** cover realtime analysis and historical reporting.

### Runtime Flow

1. The user describes a customer interaction inside Claude.
2. Claude selects an MCP tool (analyze or query).
3. The MCP server validates the payload and dispatches to the right module.
4. Analysis tools compute sentiment, extract signals, and estimate next-best actions.
5. Database tools pull aggregated metrics or history snapshots.
6. Claude receives a structured response to present back to the user.

### Why It Matters

**Without MCP**
```
User: "This customer said X, Y, Z"
Claude: "They might churn"
→ Context disappears in the next session.
```

**With MCP**
```
User: "Show me everything about ACME_CORP_001"
Claude: "4 saved analyses, trend DECLINING, latest risk high..."
→ Claude now compares trends, triggers alerts, and keeps longitudinal memory.
```

## Key Capabilities

### 1. Sentiment Evolution
- Tracks whether sentiment is improving, declining, or stable.
- Highlights inflection points and momentum shifts.

### 2. Signal Detection
- Flags pricing pressure, competitor mentions, and urgency markers.
- Generates structured notes for account managers.

### 3. Risk Forecasting
- Estimates churn probability and classifies severity.
- Suggests follow-up actions (retain, resolve, escalate).
- Auto-creates alerts when risk exceeds 70%.

### 4. Persistent Memory
- Stores every interaction with timestamps and metadata.
- Enables reporting, cohort analysis, and pattern spotting.

## Technology Stack

- **Python 3.10**
- **Anthropic MCP SDK**
- **SQLite 3**
- **TextBlob + NLTK** for lightweight NLP

## Getting Started

```powershell
pip install -r requirements.txt
python -m textblob.download_corpora
python -m nltk.downloader punkt averaged_perceptron_tagger
```

Update `%APPDATA%\Claude\claude_desktop_config.json` to point to `src/mcp_server.py`, then restart Claude Desktop.

### Usage Examples

- **Fresh analysis:**
```
These customer messages just came in:
- "Support has been great"
- "But pricing is painful"
- "Evaluating alternatives"

Is this account at risk?
```

- **Historical lookup:**
```
Show the full history for customer ACME_CORP_001.
```

- **Portfolio scan:**
```
Which of my customers are currently at high churn risk?
```

## Results

✅ Claude gains memory across sessions.
✅ Automated insights highlight risk drivers instantly.
✅ Reporting draws on historical data rather than anecdotes.

## Technical Takeaways

1. **MCP protocol** provides a clean stdio bridge into Claude.
2. **API contract design** is critical for agent-friendly tooling.
3. **NLP pipelines** can stay lightweight yet effective with TextBlob.
4. **Layered architecture** keeps analysis, persistence, and orchestration decoupled.

## Current Limitations

- Lexical sentiment model; no deep transformer yet.
- Tuned for English/Spanish inputs.
- Needs at least three messages to detect reliable trends.
- Risk estimates are probabilistic, not deterministic.

## Roadmap Ideas

- Upgrade to transformer-based classifiers.
- Ship a web dashboard for realtime monitoring.
- Push alerts via webhook or email.
- Expand multilingual coverage and entity extraction.
- Add emotion tagging (joy, anger, trust, etc.).

## Conclusion

Sentiment Evolution Tracker shows how MCP servers can extend Claude into enterprise-grade CRM assistants that remember, analyze, and act on customer history—not just the current conversation.

---

**Author:** Rubén Reyes  
**Date:** November 2025  
**Status:** ✅ Ready for review
