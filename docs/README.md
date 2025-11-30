# Sentiment Evolution Tracker – MCP Server Guide

This reference explains how to set up, operate, and extend the Sentiment Evolution Tracker. The system integrates with Claude Desktop via the Model Context Protocol (MCP) and provides persistent sentiment analytics, churn prediction, and portfolio reporting.

## Sections

- Overview
- Feature Highlights
- Installation
- Operating Checklist
- MCP Tool Contracts
- Data Model
- Troubleshooting
- Roadmap & Licensing

---

## Overview

Claude excels at single-session analysis but forgets historical context. Sentiment Evolution Tracker solves this gap with an MCP server that:

- Stores customer interactions and analyses in SQLite.
- Detects sentiment trends (rising, declining, stable).
- Calculates churn probability and surfaces alerts above configurable thresholds.
- Provides dashboards and MCP tools for portfolio-level insights.

## Feature Highlights

- Lightweight NLP pipeline (TextBlob + NLTK) for real-time scoring.
- Risk signal detection (pricing pressure, competitor mentions, frustration).
- Next-best-action recommendation (CHURN / ESCALATION / RESOLUTION / MONITOR_CLOSELY).
- Seven MCP tools covering analytics and data retrieval.
- Deterministic demo dataset for rehearsed demos or recordings.
- CLI utilities: ASCII dashboard, HTML report generator, database viewers.

## Installation

```powershell
cd mcp-nlp-server
pip install -r requirements.txt
python -m textblob.download_corpora
python -m nltk.downloader punkt averaged_perceptron_tagger
```

Register the MCP server in `%APPDATA%\Claude\claude_desktop_config.json`:

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

Restart Claude Desktop after saving the configuration.

## Operating Checklist

```powershell
python init_db.py                     # reset database (optional)
python tools\populate_demo_data.py   # load deterministic sample data
python tools\dashboard.py            # check ASCII KPIs (Ctrl+C to exit)
python tools\generate_report.py      # build data/reporte_clientes.html
python src\mcp_server.py             # start MCP server for Claude
```

Once the server is running, Claude Desktop surfaces the tools automatically.

## MCP Tool Contracts

| Tool | Purpose |
| --- | --- |
| `analyze_sentiment_evolution` | Scores each message 0–100 and labels the overall trend. |
| `detect_risk_signals` | Surfaces pricing pressure, competitor mentions, frustration phrases. |
| `predict_next_action` | Suggests the most likely outcome (churn, escalation, resolution, monitor). |
| `get_customer_history` | Returns profile data, interaction history, and open alerts. |
| `get_high_risk_customers` | Lists customers whose churn risk exceeds a threshold. |
| `get_database_statistics` | Provides portfolio KPIs (totals, active alerts, average sentiment). |
| `save_analysis` | Persists user-specified analysis results with metadata for future queries. |

## Data Model

| Table | Description |
| --- | --- |
| `customer_profiles` | Aggregated metrics per customer, including lifetime sentiment and churn risk. |
| `conversations` | Each stored analysis with timestamps, trends, predicted actions, confidence. |
| `risk_alerts` | Alerts generated when risk or thresholds exceed configured limits. |

## Troubleshooting

- **Claude cannot find the MCP server** – Verify the absolute path in `claude_desktop_config.json` and restart Claude Desktop after editing.
- **Import errors or missing modules** – Ensure the virtual environment uses Python 3.10+ and rerun `pip install -r requirements.txt`.
- **No demo data appears** – Execute `python init_db.py` followed by `python tools\populate_demo_data.py`.
- **Sentiment results feel off** – Provide at least three customer utterances and include relevant context or escalation history.

## Roadmap & Licensing

- Transformer-based sentiment and emotion tagging.
- Realtime alert delivery via Slack or email.
- Optional REST API for external integrations.
- Expanded multilingual support and PDF/CSV export routines.

The project is released under the MIT License (`LICENSE`).

Maintainer: Rubén Reyes · November 2025 · Version 1.0.0
