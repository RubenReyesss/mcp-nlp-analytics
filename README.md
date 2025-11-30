# Sentiment Evolution Tracker – MCP Monitoring Stack

Sentiment Evolution Tracker is an enterprise-ready monitoring stack that runs as a Model Context Protocol (MCP) server. It combines local sentiment analytics, churn prediction, alerting, and reporting, and can operate standalone or alongside Claude Desktop as an intelligent assistant.

## Why This Exists

Traditional “use Claude once and move on” workflows do not keep historical context, trigger alerts, or generate portfolio-level insights. Sentiment Evolution Tracker solves that by providing:

- Automated trend detection (RISING / DECLINING / STABLE)
- Churn probability scoring with configurable thresholds
- Persistent customer histories in SQLite
- Real-time alerts when risk exceeds 70%
- ASCII and HTML visualizations for demos and stakeholders
- Seven MCP tools that Claude (or any MCP-compatible LLM) can invoke on demand

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
