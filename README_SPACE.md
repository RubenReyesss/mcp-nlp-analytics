# Sentiment Evolution Tracker – Hugging Face Space Edition

MCP-powered customer sentiment monitoring packaged for Hugging Face Spaces and local demos.

> Nota: el dashboard Streamlit es opcional y no forma parte del entregable principal. Solo ejecútalo si quieres experimentar con la versión interactiva local.

## 🚀 Launch The Demo (Opcional)

```powershell
streamlit run app.py
```

Open `http://localhost:8501` for the interactive dashboard.

## 📊 Feature Set

### Interactive Dashboard
- Four KPIs (customers, analyses, sentiment, alerts).
- Two charts (churn risk vs. time, sentiment trend).
- Detailed customer table with statuses.

### Deep-Dive Panels
- Select any customer to view historical analyses.
- Inspect sentiment velocity and recommended actions.
- Highlight churn drivers automatically.

### Multi-Customer Trends
- Compare sentiment trajectories across clients.
- Identify shared risk signals.

### MCP Tooling (7 tools)
1. `analyze_sentiment_evolution`
2. `detect_risk_signals`
3. `predict_next_action`
4. `get_customer_history`
5. `get_high_risk_customers`
6. `get_database_statistics`
7. `save_analysis`

## 💻 Local Setup

Requirements: Python 3.10+, pip.

```powershell
git clone https://huggingface.co/spaces/MCP-1st-Birthday/sentiment-tracker
cd mcp-nlp-server
pip install -r requirements.txt
python init_db.py
python tools\populate_demo_data.py
python tools\dashboard.py
python tools\generate_report.py      # opens data/reporte_clientes.html
streamlit run app.py
```

## 🔧 MCP Configuration

1. Edit `config/claude_desktop_config.json`.
2. Point the server entry to `src/mcp_server.py`.
3. Restart Claude Desktop and select the sentiment tracker server.

```json
{
  "mcpServers": {
    "sentiment-tracker": {
      "command": "python",
      "args": ["src/mcp_server.py"],
      "cwd": "C:/path/to/mcp-nlp-server"
    }
  }
}
```

## 📈 Use Cases

### 1. Churn Prediction
```
Input → customer ID
Process → trend analysis + risk signals + alerts
Output → alert if risk > 70% with suggested actions
```

### 2. Real-Time Monitoring
```
Dashboard highlights:
- Critical accounts (red)
- At-risk accounts (orange)
- Healthy accounts (green)
Updated whenever new analyses are stored
```

### 3. Executive Reporting
```
Generate the HTML report to share daily:
- Risk charts
- Sentiment evolution
- Top 5 accounts needing attention
- Actionable recommendations
```

### 4. LLM Integration
```
Claude workflow:
→ get_high_risk_customers()
→ get_customer_history()
→ predict_next_action()
→ Respond with urgency, revenue at risk, and next steps
```

## 📊 Sample Dataset

- Five demo customers (manufacturing, tech, retail, healthcare, finance).
- Seventeen conversations across rising/declining/stable trends.
- Alerts triggered automatically when risk exceeds thresholds.

## 🎯 Architecture

```
User / Team Lead
        ↓
Claude Desktop (optional)
        ↓ MCP Protocol (stdio)
Sentiment Tracker Server (7 tools)
        ↓
SQLite Database (customer_profiles, conversations, risk_alerts)
```

## 🔑 Key Advantages

- **Local-first**: keep customer data on-prem.
- **Zero external APIs**: predictable cost, improved privacy.
- **Real-time**: sentiment scoring < 100 ms per request.
- **Predictive**: churn detection 5–7 days ahead.
- **Agentic**: Claude drives the workflow autonomously.
- **Scalable**: handles thousands of customers on commodity hardware.

## 📚 Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Quick Start](docs/QUICK_START.md)
- [Blog Post](../BLOG_POST.md)

## 🤝 Contributions

Suggestions are welcome—open an issue or submit a pull request.

## 📝 License

MIT License.

## 🙏 Acknowledgements

- Anthropic for MCP.
- Hugging Face for the hosting platform.
- TextBlob + NLTK for NLP utilities.

---

Built for the MCP 1st Birthday Hackathon 🎉

[GitHub](https://github.com) • [Blog](../BLOG_POST.md) • [Docs](docs/)
