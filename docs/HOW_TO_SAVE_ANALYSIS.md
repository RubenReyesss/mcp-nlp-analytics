# How To Persist Analyses In The Database

Use the dedicated MCP tool **`save_analysis`** to store results explicitly from Claude Desktop.

## Quick Instructions

### Step 1 – Ask Claude To Analyze A Conversation

Provide the full transcript and request:
1. Sentiment analysis
2. Risk detection
3. Recommended action

Example prompt:
```
Here is Ruben's conversation:

[full transcript...]

Please analyze this conversation and store the result in the database with customer_id "RUBEN".
```

### Step 2 – `save_analysis` Handles Persistence

After the analysis, instruct Claude to call the tool:

```
Use the save_analysis tool with:
- customer_id: "RUBEN"
- messages: [all conversation lines]
- sentiment_score: [0-100 score]
- trend: [RISING | DECLINING | STABLE]
- predicted_action: [CHURN | RESOLUTION | ESCALATION]
- confidence: [0.0-1.0]
```

## Full Workflow

### Option A – One Prompt

```
Do the following:
1. Analyze this customer conversation:
   [transcript...]

2. Save the results with customer_id "RUBEN" using save_analysis.

Return sentiment, trend, recommended action, and confidence.
```

### Option B – Two Prompts

Prompt 1 – Analysis:
```
Analyze this conversation and give me:
- sentiment_score
- trend
- predicted_action
- confidence
```

Prompt 2 – Persistence:
```
Great. Now store those results:
- customer_id: "RUBEN"
- messages: [conversation lines]
- sentiment_score: 48
- trend: DECLINING
- predicted_action: CHURN
- confidence: 0.85

Call the save_analysis tool.
```

## Verify The Entry

### Option 1 – CLI
```powershell
python tools/view_customer_profile.py RUBEN
```

### Option 2 – VS Code SQLite Extension
1. Open `data/sentiment_analysis.db`
2. Inspect the `conversations` table
3. Filter by `customer_id = RUBEN`

### Option 3 – HTML Report
```powershell
python tools/generate_report.py
# open data/reporte_clientes.html
```

### Option 4 – Claude Query
```
Ask get_customer_history for customer RUBEN.
```

Claude will read from SQLite and return the profile, history, and alerts.

## `save_analysis` Parameters

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| customer_id | string | Yes | Unique identifier, e.g., `RUBEN`, `ACME_CORP_001` |
| messages | array | Yes | Raw message list |
| sentiment_score | number | Yes | 0–100 normalized score |
| trend | string | Yes | `RISING`, `DECLINING`, `STABLE` |
| predicted_action | string | Yes | `CHURN`, `RESOLUTION`, `ESCALATION` |
| confidence | number | Yes | 0.0–1.0 |
| risk_level | string | No | `LOW`, `MEDIUM`, `HIGH` |
| context_type | string | No | `customer`, `employee`, `email`, etc. |

## Example – Ruben

### Prompt
```
Analyze this conversation for customer Ruben:

Customer: Hi, I need help with my account
Support: Sure, what's happening?
Customer: I've waited a week and nobody answers
Support: Sorry, checking immediately
Customer: I no longer trust this service; I'm switching providers
Support: Apologies for the delay
Customer: Too late, the decision is final

Save the analysis in the database with customer_id "RUBEN" using save_analysis.
```

### Expected Flow

1. Claude analyzes the transcript.
2. Sentiment, trend, and action are computed.
3. Claude invokes `save_analysis` with the payload.
4. SQLite stores the record under `data/sentiment_analysis.db`.

### Quick Check
```powershell
python tools/view_customer_profile.py RUBEN
```

## FAQ

**Does the save happen automatically?**  
Yes. When Claude calls `save_analysis`, the entry is written immediately.

**What if I forget the customer_id?**  
The tool rejects the call. Always provide a customer identifier.

**Can I store multiple analyses for the same customer?**  
Yes. Each call creates a new timestamped record.

**Where are the rows stored?**  
`data/sentiment_analysis.db`, table `conversations`.

**How do I review the data later?**  
Use `get_customer_history`, `tools/view_customer_profile.py`, or inspect the database directly.
