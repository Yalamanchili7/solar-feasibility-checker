# app/orchestrator/coordinator.py

import json
from app.agents.research_agent import ResearchAgent
from app.agents.permitting_agent import PermittingAgent
from app.agents.design_agent import DesignAgent
from app.utils.llm_client import LLMClient


class Orchestrator:
    """
    Orchestrates multi-agent solar feasibility evaluation:
    - Runs Research, Permitting, and Design agents
    - Aggregates their scores deterministically
    - Produces a final GO / NO_GO decision with justification
    """

    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.research_agent = ResearchAgent(self.llm)
        self.permitting_agent = PermittingAgent(self.llm)
        self.design_agent = DesignAgent(self.llm)

    # -----------------------------
    # Main evaluation function
    # -----------------------------
    def evaluate_address(self, address: str):
        print(f"\n🧠 Evaluating site feasibility for: {address}")

        research_result = self.research_agent.run(address)
        permitting_result = self.permitting_agent.run(address)
        design_result = self.design_agent.run(address)

        final_decision = self.build_final_decision(
            research_result, permitting_result, design_result
        )

        return {
            "address": address,
            "research": research_result,
            "permitting": permitting_result,
            "design": design_result,
            "final_decision": final_decision,
        }

    # -----------------------------
    # Helper: extract numeric scores
    # -----------------------------
    def _extract_score(self, data, path):
        """Safely traverse nested dicts/strings to pull numeric score."""
        cur = data
        for key in path:
            if isinstance(cur, dict):
                cur = cur.get(key)
            else:
                try:
                    cur = json.loads(cur)
                    cur = cur.get(key)
                except Exception:
                    return 50
        try:
            return int(cur)
        except Exception:
            return 50

    # -----------------------------
    # Core decision builder
    # -----------------------------
    def build_final_decision(self, research, permitting, design):
        # Extract scores
        r_score = self._extract_score(research, ["analysis", "score"])
        p_score = self._extract_score(permitting, ["permit_form", "score"])
        d_score = self._extract_score(design, ["design", "score"])

        # Weighted aggregation
        final_score = round(0.4 * r_score + 0.3 * p_score + 0.3 * d_score)

        # GO / NO_GO logic
        go_no_go = (
            "GO"
            if final_score >= 65 and all(s >= 50 for s in [r_score, p_score, d_score])
            else "NO_GO"
        )

        # Justifications (concise, deterministic)
        justifications = [
            f"Research score {r_score} reflects local policy sentiment and renewable support.",
            f"Permitting score {p_score} accounts for jurisdiction requirements and review timelines.",
            f"Design score {d_score} measures technical yield, cost efficiency, and system robustness.",
            f"Weighted overall feasibility score is {final_score}, resulting in a '{go_no_go}' decision.",
        ]

        return {
            "go_no_go": go_no_go,
            "score": final_score,
            "component_scores": {
                "research": r_score,
                "permitting": p_score,
                "design": d_score,
            },
            "justification": justifications,
        }
