---
title: MCP NLP Analytics
emoji: 📊
colorFrom: indigo
colorTo: blue
sdk: static
app_file: index.html
pinned: false
tags:
  - building-mcp-track-01
---

# Sentiment Evolution Tracker – MCP Monitoring Stack

Sentiment Evolution Tracker is an enterprise-ready monitoring stack that runs as a Model Context Protocol (MCP) server. It combines local sentiment analytics, churn prediction, alerting, and reporting, and can operate standalone or alongside Claude Desktop as an intelligent assistant.

## Why This Exists

Traditional "use Claude once and move on" workflows do not keep historical context, trigger alerts, or generate portfolio-level insights. Sentiment Evolution Tracker solves that by providing:

- Automated trend detection (RISING / DECLINING / STABLE)
- Churn probability scoring with configurable thresholds
- Persistent customer histories in SQLite
- Real-time alerts when risk exceeds 70%
- ASCII and HTML visualizations for demos and stakeholders
- Seven MCP tools that Claude (or any MCP-compatible LLM) can invoke on demand

## 🎥 Demo Video

A demo video (3-4 minutes) showing live sentiment analysis, risk detection, and MCP integration with Claude:

**[Watch on YouTube](https://youtu.be/h2tNu2KTPQk)**

The video demonstrates:
- Live sentiment analysis of customer conversations
- Risk detection and churn prediction
- MCP tool invocation via Claude Desktop
- Real-time alerts and reporting

---

## How to Use

### Quick Start (5 minutes)

1. **Clone and install:**
   ```powershell
   git clone https://github.com/RubenReyesss/mcp-nlp-analytics.git
   cd mcp-nlp-server
   pip install -r requirements.txt
   python -m textblob.download_corpora
   python -m nltk.downloader punkt averaged_perceptron_tagger
   ```

2. **Populate demo data:**
   ```powershell
   python init_db.py
   python tools/populate_demo_data.py
   ```

3. **View dashboard:**
   ```powershell
   python tools/dashboard.py
   ```

4. **Generate HTML report:**
   ```powershell
   python tools/generate_report.py
   # Opens data/reporte_clientes.html in your browser
   ```

5. **Integrate with Claude Desktop:**
   - Edit `config/claude_desktop_config.json` with your actual path
   - Restart Claude Desktop
   - Start the MCP server: `python src/mcp_server.py`
   - Now Claude can access all 7 sentiment analysis tools

---

## Installation

```powershell
cd mcp-nlp-server
pip install -r requirements.txt
python -m textblob.download_corpora
python -m nltk.downloader punkt averaged_perceptron_tagger
```

## Daily Operations

- `python init_db.py` – rebuilds the database from scratch (reset option)
- `python tools\populate_demo_data.py` – loads deterministic demo customers
- `python tools\dashboard.py` – terminal dashboard (Ctrl+C to exit)
- `python tools\generate_report.py` – creates `data/reporte_clientes.html`
- `python src\mcp_server.py` – launch the MCP server for Claude Desktop

## MCP Tool Suite

| Tool | Purpose |
| --- | --- |
| `analyze_sentiment_evolution` | Calculates sentiment trajectory for a set of messages |
| `detect_risk_signals` | Flags phrases that correlate with churn or dissatisfaction |
| `predict_next_action` | Forecasts CHURN / ESCALATION / RESOLUTION outcomes |
| `get_customer_history` | Retrieves full timeline, sentiment, and alerts for a customer |
| `get_high_risk_customers` | Returns customers whose churn risk is above a threshold |
| `get_database_statistics` | Portfolio-level KPIs (customers, alerts, sentiment mean) |
| `save_analysis` | Persists a custom analysis entry with full metadata |

## Data Model (SQLite)

- `customer_profiles` – customer metadata, lifetime sentiment, churn risk, timestamps
- `conversations` – every analysis entry, trend, predicted action, confidence
- `risk_alerts` – generated alerts with severity, notes, and resolution state

Database files live in `data/sentiment_analysis.db`; scripts automatically create the directory if needed.

## Claude Desktop Integration

`config/claude_desktop_config.json` registers the server:

```json
{
  "mcpServers": {
    "sentiment-tracker": {
      "command": "python",
      "args": ["src/mcp_server.py"],
      "cwd": "C:/Users/Ruben Reyes/Desktop/MCP_1stHF/mcp-nlp-server"
    }
  }
}
```

Restart Claude Desktop after editing the file. Once connected, the seven tools above appear automatically and can be invoked using natural language prompts.

## Documentation Map

- `docs/QUICK_START.md` – five-minute functional checklist
- `docs/ARCHITECTURE.md` – diagrams, module responsibilities, data flow
- `docs/HOW_TO_SAVE_ANALYSIS.md` – practical guide for the `save_analysis` tool
- `docs/EXECUTIVE_SUMMARY.md` – executive briefing for stakeholders
- `docs/CHECKLIST_FINAL.md` – submission readiness checklist

## Tech Stack

- Python 3.10+
- MCP SDK 0.1+
- SQLite (standard library)
- TextBlob 0.17.x + NLTK 3.8.x
- Chart.js for optional HTML visualizations

## Status

- ✅ Production-style folder layout
- ✅ Deterministic demo dataset for the hackathon video
- ✅ Comprehensive English documentation
- ✅ Tests for the `save_analysis` workflow (`tests/test_save_analysis.py`)

Run `python tools\dashboard.py` or open the generated HTML report to verify data before your demo, then start the MCP server and launch Claude Desktop to show the agentic workflow in real time.

---

## Team

| Role | Contributor | GitHub |
|------|-------------|--------|
| **Developer** | RubenReyesss | [@RubenReyesss](https://github.com/RubenReyesss) |

---

## Track

This project is submitted to **Track 1: Building MCPs** (`building-mcp-track-01`).

It demonstrates a production-ready MCP server that extends Claude's capabilities with persistent analytics, risk prediction, and alerting—solving the limitation that Claude lacks memory, database writes, and automated monitoring.

---

## 📱 Social Media Post

**Announcement on LinkedIn:**

[Read the full post on LinkedIn](https://www.linkedin.com/posts/rubenreyesparra_mcp-nlp-analytics-a-hugging-face-space-activity-7400976539959390208-SG3Q?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFIWAmYBYY2kpr1rhopcOJoKJgl2HvUdM-8)

Featured in: MCP 1st Birthday Hackathon

---

## Resources

- **GitHub Repository:** https://github.com/RubenReyesss/mcp-nlp-analytics
- **Hugging Face Space:** https://huggingface.co/spaces/MCP-1st-Birthday/mcp-nlp-analytics
- **Demo Video:** https://youtu.be/h2tNu2KTPQk
- **LinkedIn Post:** https://www.linkedin.com/posts/rubenreyesparra_mcp-nlp-analytics-a-hugging-face-space-activity-7400976539959390208-SG3Q

---

Made with ❤️ for the Anthropic MCP 1st Birthday Hackathon
