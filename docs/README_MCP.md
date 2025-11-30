# Sentiment Evolution Tracker

## Purpose

A Claude Desktop extension that tracks customer sentiment over time with persistent memory. Claude gains the ability to remember customer histories across sessions.

## The Gap

Standard Claude usage:
- Brilliant single-turn analysis ✅
- Forgets everything after the chat ❌
- Cannot compare customers across conversations ❌
- Lacks historical reporting ❌

## The Solution

This MCP server exposes six domain-specific tools:

### Realtime Analysis Tools
1. **Sentiment Evolution** – Detects whether sentiment is improving, declining, or stable.
2. **Risk Signal Detection** – Flags pricing pressure, competitor mentions, frustration markers.
3. **Next Action Prediction** – Suggests whether to escalate, retain, or close.

### Historical Intelligence Tools
4. **Customer History** – Retrieves stored analyses for a customer.
5. **High-Risk Customers** – Lists accounts trending toward churn.
6. **Portfolio Statistics** – Summarizes overall health metrics.

## High-Level Flow

```
User describes customer interaction
                ↓
Claude selects the appropriate tool
                ↓
MCP server runs analysis or database query
                ↓
Results persist to SQLite
                ↓
Claude returns structured insights
```

## Practical Example

**Prompt:**
```
Customer messages:
- "Service is excellent"
- "Pricing is higher than the competition"
- "Considering a switch"

Are they at risk?
```

**Automatic pipeline:**
1. Sentiment shifts from 57 → 43/100 (trend `DECLINING`).
2. Signals highlight competitor mention and potential churn.
3. Recommended action: `MONITOR_CLOSELY` with 65% confidence.
4. Analysis is stored in the database.
5. If risk > 70%, an alert is created.

**Claude responds:**
```
Medium risk detected:
- Declining sentiment trajectory
- Explicit competitor comparison
- Action: urgent outreach and pricing review
```

## Why It Matters

**Without MCP**
- Claude only reflects the current conversation.
- Historical context is lost.
- No portfolio-level reporting.

**With MCP**
- Persistent memory across customers ✅
- Trend comparisons over time ✅
- Automated alert generation ✅
- Portfolio dashboards ✅

## Real-World Scenario

**Day 1 – New customer "Juan García"**
```
Sentiment: STABLE at 70/100
Risk: Low
Record stored in SQLite
```

**Day 7 – Follow-up from Juan García**
```
Message: "Pricing is too high; I might switch"
Sentiment drops to 43/100 → trend DECLINING
Risk moves to MEDIUM
Alert generated automatically
```

**Outcome:**
- Detects customer sentiment shifts immediately.
- Maintains full conversation history.
- Surfaces alerts before churn occurs.
- Enables data-driven retention strategies.

## Technology Stack

- **Python 3.10** for orchestration.
- **Anthropic MCP** for Claude integration.
- **SQLite** for persistent storage.
- **TextBlob + NLTK** delivering lightweight NLP.

## Feature Highlights

✅ Automated sentiment scoring  
✅ Risk signal detection  
✅ Churn prediction with recommended actions  
✅ Persistent customer histories  
✅ Alert generation when thresholds are crossed  
✅ Portfolio-level reporting  

## Quick Installation

1. `pip install -r requirements.txt`
2. `python -m nltk.downloader punkt`
3. Register the server in Claude Desktop config.
4. Restart Claude to apply.

## Current Limitations

- Lexical sentiment model (no deep transformer yet).
- Optimized for English and Spanish.
- Probabilistic scoring; not deterministic.
- Works best with conversations ≥ 3 messages.

## Roadmap

- Transformer-based sentiment and emotion detection.
- Web dashboard for live monitoring.
- Realtime notifications (Slack/email/webhook).
- Expanded multilingual support.
- Fine-grained emotion tagging.

## Value Proposition

1. **Data persistence** – Claude remembers customers across sessions.
2. **Historical analytics** – Track trends instead of snapshots.
3. **Automation** – Alerts and predictions run autonomously.
4. **Scalability** – Moves from single-use analysis to enterprise tooling.

## Closing Thoughts

Sentiment Evolution Tracker is a production-ready MCP server proving how custom tools can elevate Claude from conversational analysis to strategic customer intelligence.

---

**Ready to try it?** The repository ships with demo data and scripts.

---

Rubén Reyes · November 2025 · v1.0
