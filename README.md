# Solar Site Feasibility Multi-Agent System
*A technical challenge implementation by **Sundeep Yalamanchili***

---

## Overview

This project is a **multi-agent AI system** that evaluates the **feasibility of solar projects** for given addresses.  
Each agent operates independently to analyze a specific aspect of a site — policy environment, permitting requirements, and design potential — and the orchestrator combines those findings into a final **Go / No-Go** decision.

It’s designed as a realistic, modular prototype that could be expanded into a production pipeline using real data sources and LLM-powered reasoning.

---

## Goals

The system implements everything requested in the **Climatize AI/ML Engineering Lead Technical Challenge**, including:

- A working proof-of-concept that accepts one or more addresses and returns a **feasibility score + justification**.  
- Multiple **independent agents** communicating through a lightweight orchestrator.  
- Human-readable outputs (CLI + optional Streamlit UI).  
- A clean, dockerized, reproducible environment.

---

## Architecture



agent_system/
├── src/
│ ├── agents/
│ │ ├── research_agent.py
│ │ ├── permitting_agent.py
│ │ └── design_agent.py
│ │
│ ├── utils/
│ │ ├── geo.py
│ │ ├── io.py
│ │ └── scoring.py
│ │
│ ├── ui/
│ │ └── app.py
│ │
│ ├── data/
│ │ ├── dummy_permit_rules.json
│ │ ├── mock_solar_irradiance.csv
│ │ └── permit_form_template.json
│ │
│ ├── orchestrator.py
│ ├── main.py
│ └── models.py
│
├── tests/
│ └── smoke_test.py
│
├── requirements.txt
├── Dockerfile
├── pytest.ini
└── README.md



---

### Agent Responsibilities

| Agent | Role | Key Output |
|--------|------|------------|
| **Research Agent** | Simulates querying public policy/news data. Summarizes if region is favorable for solar. | `ResearchResult` (boolean + summary) |
| **Permitting Agent** | Classifies jurisdiction, fetches dummy permitting rules, and auto-fills form fields. | `PermittingResult` (form + readiness score) |
| **Design Agent** | Estimates system size and annual yield using mock irradiance data. | `DesignResult` (capacity, yield, BoM) |

The **Orchestrator** runs all agents asynchronously and aggregates their results into a final **composite score** and decision.

---

## Scoring Logic

| Component | Weight | Criteria |
|------------|---------|----------|
| Research | 40 pts | Favorable local policy, incentives, or no moratoriums |
| Permitting | 30 pts | Readiness score from auto-filled permit form |
| Design | 30 pts | ≥ 3 kW capacity and ≥ 3000 kWh/yr yield |

Total score ≤ 100 →  
**≥ 70 = GO**, otherwise **NO-GO**.

---

## Running Locally

### 1️⃣ Setup Environment
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt


2 Run a Test Address

python -m src.main --addresses "123 Solar Way, Phoenix, AZ"

Sample Output
Address: 123 Solar Way, Phoenix, AZ
Decision: GO (94)

Agent Summary
Research   → Positive signals and no moratoriums.
Permitting → Phoenix, AZ (80/100)
Design     → 9.84 kW → 17318 kWh/yr

 • Policy signals favorable.
 • Permitting looks feasible with standard docs.
 • Design capacity acceptable.
 • Composite score: 94


3 Streamlit UI (Optional)

streamlit run src/ui/app.py


4 Run Tests

 PYTHONPATH=. pytest -q

Expected Output
.                                                                 [100%]
1 passed in 0.7s


---

## Reflection & Limitations

This project was built as a realistic proof-of-concept rather than a production pipeline.  
The focus was on **architecture, reasoning, and clarity**, not on building a full data integration stack.

I intentionally mocked most external data sources to keep the system reproducible and transparent.  
For example, the Research Agent uses simulated policy data instead of scraping live news, and the Permitting Agent loads dummy rules instead of calling real municipal APIs.  
This allowed me to focus on how independent agents would communicate, reason, and merge their findings — which is the actual goal of the challenge.

If extended beyond the scope of this task, I would:
- Plug the Research Agent into a real policy/news API and use an LLM for summarization.
- Integrate NREL’s PVWatts or satellite imagery for the Design Agent.
- Auto-generate PDF permit forms from the Permitting Agent’s JSON.
- Add richer inter-agent communication and caching between runs.

Overall, I’m happy with how the system came together — it’s modular, explainable, and deployable, which is what a real-world AI engineering team would need as a foundation for production-grade agent systems.