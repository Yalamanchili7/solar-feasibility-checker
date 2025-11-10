# ☀️ Solar Site Feasibility Multi-Agent System
*A technical challenge implementation by **Sundeep Yalamanchili***

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/container-Docker-2496ED.svg)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/tests-GitHub%20Actions-success.svg)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Overview

This project is a **multi-agent AI system** that evaluates the **feasibility of solar projects** for given addresses.  
Each agent operates independently to analyze a specific aspect of a site — policy environment, permitting requirements, and design potential — and the orchestrator combines those findings into a final **Go / No-Go** decision.

It's designed as a realistic, modular prototype that could be expanded into a production pipeline using real data sources and LLM-powered reasoning.

---

## Goals

The system implements everything requested in the **Climatize AI/ML Engineering Lead Technical Challenge**, including:

- A working proof-of-concept that accepts one or more addresses and returns a **feasibility score + justification**.  
- Multiple **independent agents** communicating through a lightweight orchestrator.  
- Human-readable outputs (CLI + optional Streamlit UI).  
- A clean, dockerized, reproducible environment.

---

## Architecture

```
agent_system/
├── src/
│   ├── agents/
│   │   ├── research_agent.py
│   │   ├── permitting_agent.py
│   │   └── design_agent.py
│   │
│   ├── utils/
│   │   ├── geo.py
│   │   ├── io.py
│   │   └── scoring.py
│   │
│   ├── ui/
│   │   └── app.py
│   │
│   ├── data/
│   │   ├── dummy_permit_rules.json
│   │   ├── mock_solar_irradiance.csv
│   │   └── permit_form_template.json
│   │
│   ├── orchestrator.py
│   ├── main.py
│   └── models.py
│
├── tests/
│   └── smoke_test.py
│
├── requirements.txt
├── Dockerfile
├── pytest.ini
└── README.md
```

---

## Agent Responsibilities

| Agent | Role | Key Output |
|--------|------|------------|
| **Research Agent** | Analyzes local policy signals (using dummy data). Summarizes if region is favorable for solar. | `ResearchResult` (boolean + rationale) |
| **Permitting Agent** | Loads mock permitting rules and auto-fills permit forms. | `PermittingResult` (form + readiness score) |
| **Design Agent** | Estimates system capacity and annual yield using mock irradiance data. | `DesignResult` (capacity, yield, BoM) |

The **Orchestrator** runs all agents asynchronously and merges their findings into a **composite score** and final decision.

---

## Scoring Logic

| Component | Weight | Criteria |
|------------|---------|----------|
| Research | 40% | Favorable local policy, incentives, or no moratoriums |
| Permitting | 30% | Readiness score from auto-filled permit form |
| Design | 30% | ≥ 3 kW capacity and ≥ 3000 kWh/yr yield |

**Composite ≥ 70 → GO**  
**Composite < 70 → NO-GO**

---

## ⚙️ Running Locally

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Yalamanchili7/solar-feasibility-checker.git
cd solar-feasibility-checker
```

### 2️⃣ Create and Activate a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Run the CLI Feasibility Checker

```bash
export PYTHONPATH=.
python -m src.main --address "1207 E 8th St, Tempe, AZ"
```

**✅ Expected Output**

```
🔆 Running Solar Feasibility Check...

╭───────────── Result ──────────────╮
│ Address: 1207 E 8th St, Tempe, AZ │
│ Decision: GO (74.5)               │
╰───────────────────────────────────╯
                                  Agent Summary                                  
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Agent      ┃ Summary                                                          ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Research   │ Favorable policy environment for solar.                         │
│ Permitting │ Tempe, AZ (80/100)                                              │
│ Design     │ 9.84 kW → 16531.0 kWh/yr                                        │
└────────────┴──────────────────────────────────────────────────────────────────┘
✅ Site looks feasible for solar installation!
```

A JSON report will be created under `outputs/`.

### 5️⃣ Run the Streamlit Web App

```bash
streamlit run src/ui/app.py
```

Then open your browser to:

👉 **http://localhost:8501**

Enter a full address (e.g., `1207 E 8th St, Tempe, AZ`) and click  
**Run Feasibility Check** to see results visually.

### 6️⃣ Run Unit Tests (Optional)

```bash
pytest -q
```

**✅ Expected Output**

```
.                                                                   [100%]
1 passed in 0.7s
```

### 7️⃣ Run with Docker (Optional)

If you prefer to containerize the app:

```bash
docker build -t solar-feasibility-checker .
docker run -p 8501:8501 solar-feasibility-checker
```

Then open your browser at:  
👉 **http://localhost:8501**

---

## 💬 Reflection & Limitations

This project was built as a **realistic proof-of-concept** rather than a production pipeline.  
The focus was on **architecture, reasoning, and clarity**, not on full data integrations.

**Mock data** ensures reproducibility while demonstrating how independent agents can coordinate.  
If expanded, next steps would include:

- **Connecting the Research Agent** to live policy/news APIs and LLM summarization.

- **Using NREL PVWatts** or satellite imagery for more accurate irradiance modeling.

- **Auto-generating PDF permit forms** from the permitting JSON.

- **Adding richer inter-agent communication** and caching layers.

---

## 🧾 License

This project is released under the **MIT License** — feel free to fork, modify, and extend it.