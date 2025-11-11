# ☀️ Solar Site Feasibility Multi-Agent System
*A technical challenge implementation by **Sundeep Yalamanchili***

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/container-Docker-2496ED.svg)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/tests-GitHub%20Actions-success.svg)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)


## 🌞 Overview

The system orchestrates multiple specialized agents that each analyze different aspects of solar feasibility:

| Agent | Function | Key Output |
|--------|-----------|------------|
| **Research Agent** | Analyzes recent policy, sentiment, and renewable energy trends for the location. | Summary, sentiment, risk factors, and a favorability score. |
| **Permitting Agent** | Looks up local building/electrical permitting rules and fire setback codes. | Required permits, review times, and a permitting score. |
| **Design Agent** | Uses NREL’s PVWatts API + LLM design reasoning to estimate solar yield and system components. | System size, annual production, BoM, and design score. |

The **Orchestrator** combines these analyses into a final decision:
> 🧠 Weighted scoring: Research (40%) + Permitting (30%) + Design (30%)

---

## ⚙️ System Architecture

```
solar-feasibility-checker/
├── app/
│   ├── agents/
│   │   ├── research_agent.py
│   │   ├── permitting_agent.py
│   │   └── design_agent.py
│   ├── orchestrator/
│   │   └── coordinator.py
│   ├── utils/
│   │   ├── llm_client.py
│   │   ├── config.py
│   │   └── geocode.py
│   └── data/
│       └── permitting_rules.csv
├── outputs/
│   ├── logs/
│   │   ├── research_agent/
│   │   ├── permitting_agent/
│   │   └── design_agent/
│   └── output_<city>_<timestamp>.json
├── cli.py
└── README.md
```

---

## 🚀 Quick Start

### 1️⃣ Setup Environment
```bash
git clone https://github.com/Yalamanchili7/solar-feasibility-checker.git
cd solar-feasibility-checker
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Add API Keys

Create `.env` or set environment variables:
```bash
export OPENAI_API_KEY="your_openai_key_here"
export NREL_API_KEY="your_nrel_key_here"
export NEWS_API_KEY="news_api_key"
```

These are used by:
- `app/utils/llm_client.py` → OpenAI GPT-4o-mini  
- `app/utils/config.py` → NREL PVWatts API

### 3️⃣ Run the System
```bash
python cli.py --address "Phoenix, AZ" --save
```

Example output:
```
🌞 Running Solar Feasibility Analysis for: Phoenix, AZ
✅ Matched permitting rule for phoenix
✅ Final Decision: GO (Score: 72)
💾 Results saved to: outputs/output_Phoenix_AZ_20251111_1930.json
```

---

## 🧩 How It Works

1. **Research Agent**
   - Scrapes recent renewable energy headlines & policy sentiment.
   - Extracts tone, risks, and computes a “favorability score”.

2. **Permitting Agent**
   - Loads permitting rules from `app/data/permitting_rules.csv`.
   - Determines which permits are required, expected delays, and friendliness.
   - Computes a **permit friendliness score (0–100)**.

3. **Design Agent**
   - Uses geocoding + NREL PVWatts to estimate solar production.
   - LLM generates the **Bill of Materials** and engineering notes.
   - Produces a design performance score.

4. **Orchestrator**
   - Integrates agent results.
   - Runs a final GPT evaluation to produce a `GO` or `NO_GO` decision.

---

## 🧠 Example Decision Output

```json
{
  "go_no_go": "GO",
  "score": 72,
  "component_scores": {
    "research": 75,
    "permitting": 60,
    "design": 80
  },
  "justification": [
    "Research score 75 reflects supportive policy sentiment.",
    "Permitting score 60 accounts for manageable jurisdiction requirements.",
    "Design score 80 reflects strong yield and system robustness."
  ]
}
```

---

## 🧪 Testing Scenarios

You can easily test multiple addresses:

```bash
python cli.py --address "Austin, TX" --save
python cli.py --address "Seattle, WA" --save
python cli.py --address "Miami, FL" --save
python cli.py --address "Denver, CO" --save
```

All results are stored in:
```
outputs/output_<city>_<timestamp>.json
```

---

## 📊 Scoring Methodology

| Component | Weight | Factors |
|------------|--------|----------|
| **Research** | 40% | Policy sentiment, regulatory support, risks |
| **Permitting** | 30% | Review time, required permits, fire code |
| **Design** | 30% | Yield, capacity, equipment, shading, cost |

The final score is an aggregate:
```
total = (research * 0.4) + (permitting * 0.3) + (design * 0.3)
```

---

## 🧾 Logging

Each agent logs detailed runs in:
```
outputs/logs/<agent_name>/
```

Including:
- Raw LLM prompts/responses
- Parsed JSON
- Computed scores
- Fallback flags (if any)

---

## 🧱 Tech Stack

- **Python 3.11**
- **OpenAI GPT-4o-mini** (LLM reasoning)
- **NREL PVWatts API** (solar energy modeling)
- **Pandas**, **Requests**, **JSON**, **Argparse**
- **Structured Logging + Fallback Error Handling**

---

## 🌍 Next Steps (Future Enhancements)

- 🔁 Add caching for policy/news scraping  
- 🗺️ Integrate GIS-based shading analysis  
- 🧩 Fine-tune JSON schema validation  
- 💬 Stream LLM outputs in real-time for UI integration  

---

## 💡 Author
**Sundeep Yalamanchili**  

