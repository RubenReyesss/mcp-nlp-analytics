# Quick Verification Guide – Sentiment Evolution Tracker

Use this guide to validate the project in under five minutes before recording or presenting.

---

## ⚡ Fast Track Checklist (≈5 minutes)

### 1. Environment (1 minute)

```powershell
python --version            # confirm Python 3.10+

```

### 2. NLP Assets (2 minutes)

```powershell
python -m textblob.download_corpora
python -m nltk.downloader punkt averaged_perceptron_tagger
```

### 3. Claude Desktop Wiring (2 minutes)

1. Open `%APPDATA%\Claude\claude_desktop_config.json`
2. Point the MCP entry to `src/mcp_server.py`
3. Save, close Claude completely, and relaunch (wait 30–40 seconds)

---

## ✅ Claude Smoke Tests

Run these prompts in Claude Desktop (server running via `python src\mcp_server.py`).

### Test 1 – Baseline Analysis (~30 s)
```
Analyze these customer messages:
- "I love your product"
- "but the price is too high"
- "I'm looking at alternatives"

Use analyze_sentiment_evolution, detect_risk_signals, and predict_next_action.
```
Expected: DECLINING sentiment, MEDIUM risk, MONITOR_CLOSELY recommendation.

### Test 2 – Portfolio KPIs (~30 s)
```
Use get_database_statistics to tell me how many customers I have, how many are at risk, and the average sentiment.
```
Expected: 5 customers, 1 high-risk customer, average sentiment ≈ 68.

### Test 3 – Customer History (~30 s)
```
Use get_customer_history with customer_id "ACME_CORP_001" and show the full history.
```
Expected: Detailed profile, multiple analyses, active alerts.

### Test 4 – High-Risk Filter (~30 s)
```
Use get_high_risk_customers with threshold 0.5 and list the clients.
```
Expected: ACME_CORP_001 flagged at 85% risk.

---

## 📊 Technical Verification

### Confirm the MCP Server Is Alive

```powershell
Get-Process | Where-Object {$_.Name -like "*python*"} | Format-Table ProcessName, Id
```
You should see the Python process running the MCP server.

### Inspect the Database

```powershell
python - <<'PY'
import sqlite3
conn = sqlite3.connect('data/sentiment_analysis.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM conversations')
print('Conversations:', cur.fetchone()[0])
conn.close()
PY
```
Expect a non-zero conversation count after loading demo data.

---

## 🎯 Acceptance Criteria

- **Functionality** – All seven MCP tools execute without errors and persist data.
- **Claude Integration** – MCP server appears in Claude, and tool calls return coherent answers.
- **Value Demonstrated** – Historical analytics, alerts, and actions are visible.
- **Code Quality** – Modular structure, error handling, and documentation present.

---

## 🚨 Troubleshooting

- Claude cannot see the server → verify the path in `claude_desktop_config.json`, restart Claude.
- Tool invocation fails → ensure dependencies are installed with Python 3.10+.
- Empty database → rerun `python init_db.py` and `python tools\populate_demo_data.py`.
- Import errors → run commands from the `mcp-nlp-server` folder.

---

## 📁 Relevant Files

```
mcp-nlp-server/
├── README.md                  # full technical reference
├── docs/ARCHITECTURE.md       # architecture diagram and flow
├── docs/EXECUTIVE_SUMMARY.md  # stakeholder briefing
├── requirements.txt           # dependencies
├── data/sentiment_analysis.db # generated database
└── src/                       # MCP server and analysis modules
```

---

## 💡 What Makes This Different

- Maintains persistent customer histories for Claude.
- Enables queries across the entire portfolio, not just the current chat.
- Demonstrates how MCP tooling unlocks agentic workflows with saved state.

---

## 📞 Technical Snapshot

| Item | Detail |
| --- | --- |
| Language | Python 3.10+ |
| MCP SDK | 0.1.x |
| Database | SQLite 3 |
| MCP Tools | 7 |
| Response Time | < 100 ms per tool call on demo data |

---

For deeper documentation see `README.md` and the architecture notes in `docs/`.
### 4. Código ✅
