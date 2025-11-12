import os
import json
import pandas as pd
from datetime import datetime
from app.utils.llm_client import LLMClient

LOG_DIR = "outputs/logs/permitting_agent"
os.makedirs(LOG_DIR, exist_ok=True)


class PermittingAgent:
    """Generates a filled permit form and assesses local permitting friendliness."""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

        # --- Robust relative path handling ---
        rules_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "permitting_rules.csv"
        )
        rules_path = os.path.abspath(rules_path)
        print(f"📂 Loading permitting rules from: {rules_path}")

        if not os.path.exists(rules_path):
            print("⚠️ permitting_rules.csv not found — using empty fallback DataFrame.")
            self.rules = pd.DataFrame(
                columns=[
                    "state",
                    "jurisdiction",
                    "building_permit",
                    "electrical_permit",
                    "fire_setback",
                    "avg_review_days",
                ]
            )
        else:
            self.rules = pd.read_csv(rules_path)

    # -----------------------------
    # STEP 1: Match location to rule set
    # -----------------------------
    def get_rules_for_location(self, address: str):
        city = address.split(",")[0].strip().lower()

        if "jurisdiction" not in self.rules.columns:
            print("⚠️ CSV missing 'jurisdiction' column — returning default rule.")
            return self.default_rules(city)

        row = self.rules[self.rules["jurisdiction"].str.lower() == city]

        if row.empty:
            print(f"⚠️ No permitting rule found for '{city}', using default fallback.")
            return self.default_rules(city)

        rules = row.iloc[0].to_dict()
        print(f"✅ Matched permitting rule for {city}: {rules}")
        return rules

    def default_rules(self, city):
        return {
            "jurisdiction": city,
            "building_permit": True,
            "electrical_permit": True,
            "fire_setback": 18,
            "avg_review_days": 10,
        }

    # -----------------------------
    # STEP 2: Generate permit form with LLM
    # -----------------------------
    def generate_permit_form(self, address: str, rules: dict):
        system_prompt = (
            "You are a solar permitting specialist. "
            "Given local permitting rules, fill out a simple permit form."
        )

        user_prompt = f"""
Address: {address}
Rules:
{json.dumps(rules, indent=2)}

Respond strictly in JSON with:
  - permit_required
  - fire_code_setback_inches
  - average_review_days
  - special_considerations
"""

        raw_response = self.llm.chat(system_prompt, user_prompt)

        try:
            form = json.loads(raw_response)
        except json.JSONDecodeError:
            print("⚠️ LLM returned invalid JSON — using fallback.")
            permits = []
            if rules.get("building_permit"):
                permits.append("building")
            if rules.get("electrical_permit"):
                permits.append("electrical")

            form = {
                "permit_required": permits or ["electrical"],
                "fire_code_setback_inches": rules.get("fire_setback", 18),
                "average_review_days": rules.get("avg_review_days", 10),
                "special_considerations": "Fallback due to invalid LLM output.",
            }

        # --- Normalize and enrich ---
        form = self._normalize_permit_fields(form)   # 🔧 NEW LINE
        form.setdefault("permit_required", ["electrical"])
        form.setdefault("fire_code_setback_inches", 18)
        form.setdefault("average_review_days", 10)
        form.setdefault("special_considerations", "None noted.")
        form["score"] = self.compute_permit_score(form)
        form["jurisdiction"] = rules.get("jurisdiction", "Unknown")

        permits = ", ".join(form.get("permit_required", []))
        form["friendly_notes"] = (
            f"{rules.get('jurisdiction', 'This jurisdiction')} typically requires "
            f"{permits or 'standard permits'} with an average review time of "
            f"{form.get('average_review_days', 'N/A')} days and a "
            f"fire code setback of {form.get('fire_code_setback_inches', 'N/A')} inches."
        )

        log_path = os.path.join(
            LOG_DIR, f"{address.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(log_path, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "address": address,
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "raw_response": raw_response,
                    "parsed_form": form,
                },
                f,
                indent=2,
            )

        return form

    # -----------------------------
    # STEP 3: Compute permit friendliness score
    # -----------------------------
    def compute_permit_score(self, form: dict) -> int:
        days = form.get("average_review_days", 10)
        required = len(form.get("permit_required", []))
        setback = form.get("fire_code_setback_inches", 18)

        score = 100 - (days * 2.5) - (required * 10) - (max(0, setback - 20) * 0.5)
        return max(0, min(100, int(score)))

    # -----------------------------
    # STEP 4: Full pipeline
    # -----------------------------
    def run(self, address: str):
        print(f"🏗️ Running PermittingAgent for: {address}")

        try:
            rules = self.get_rules_for_location(address)
            permit_form = self.generate_permit_form(address, rules)
        except Exception as e:
            print(f"❌ PermittingAgent error: {e}")
            rules = {}
            permit_form = {
                "summary": f"Error occurred: {e}",
                "score": 0,
                "special_considerations": "Error in pipeline.",
            }

        return {
            "agent": "PermittingAgent",
            "address": address,
            "rules": rules,
            "permit_form": permit_form,
            "friendly_notes": permit_form.get("friendly_notes", "")
        }

    # -----------------------------
    # STEP 5: Normalize permit field 
    # -----------------------------
    def _normalize_permit_fields(self, form: dict) -> dict:
        """Ensure permit_required is always a list for consistent CLI output."""
        permits = form.get("permit_required", [])
        if isinstance(permits, str):
            permits = [p.strip() for p in permits.split(",") if p.strip()]
        elif not isinstance(permits, list):
            permits = [str(permits)]
        form["permit_required"] = permits
        return form
