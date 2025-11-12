# web/app.py
import os
import sys
import json
import streamlit as st

# --- Fix import path ---
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from cli import parse_json_block
from app.utils.llm_client import LLMClient
from app.orchestrator.coordinator import Orchestrator


# ---------------- Streamlit Layout ----------------
st.set_page_config(page_title="Solar Feasibility Checker", page_icon="🌞", layout="centered")

st.title("🏗️ Solar Feasibility Checker — Multi-Agent LLM System")
st.caption("Analyze a site’s solar project feasibility using AI-powered research, permitting, and design agents.")

address = st.text_input("📍 Enter Site Address", placeholder="e.g., 123 Main St, Austin, TX")
save_output = st.checkbox("💾 Save full JSON output to /outputs folder", value=True)


# ---------------- UI Helpers ----------------
def color_score(score):
    """Return HTML color badge for score ranges."""
    if score >= 80:
        color = "#4CAF50"  # green
    elif score >= 60:
        color = "#FFB300"  # amber
    else:
        color = "#E53935"  # red
    return f"<span style='background:{color}; padding:4px 10px; border-radius:10px; color:white;'>{score}</span>"


def render_section(title, data, summary_fields=None):
    """Display collapsible, formatted sections."""
    with st.expander(title, expanded=True):
        score = data.get("score")
        if score is not None:
            st.markdown(f"**Score:** {color_score(score)}", unsafe_allow_html=True)

        if summary_fields:
            for field, label in summary_fields.items():
                val = data.get(field)
                if isinstance(val, (list, dict)):
                    st.json(val)
                else:
                    st.markdown(f"**{label}:** {val if val else 'N/A'}")

        st.markdown("**Raw JSON:**")
        st.json(data)


# ---------------- Run Analysis ----------------
if st.button("🚀 Run Analysis"):
    if not address.strip():
        st.warning("Please enter a valid address.")
        st.stop()

    st.info(f"Running Solar Feasibility Analysis for **{address}** — this may take up to a minute...")
    try:
        llm = LLMClient()
        orchestrator = Orchestrator(llm)
        result = orchestrator.evaluate_address(address)

        st.success("✅ Analysis Complete!")

        # --- Research Agent ---
        research_data = parse_json_block(result.get("research", {}).get("analysis", {}))
        render_section(
            "🔍 Research Agent Summary",
            research_data,
            {
                "summary": "Summary",
                "sentiment": "Sentiment",
                "risks": "Risks",
            },
        )

        # --- Permitting Agent ---
        permit_data = parse_json_block(result.get("permitting", {}).get("permit_form", {}))
        render_section(
            "🏗️ Permitting Agent Summary",
            permit_data,
            {
                "jurisdiction": "Jurisdiction",
                "permit_required": "Required Permits",
                "average_review_days": "Avg Review Days",
                "fire_code_setback_inches": "Fire Setback (inches)",
                "friendly_notes": "Notes",
            },
        )

        # --- Design Agent ---
        design_data = parse_json_block(result.get("design", {}).get("design", {}))
        render_section(
            "📐 Design Agent Summary",
            design_data,
            {
                "system_capacity_kwdc": "Capacity (kWdc)",
                "annual_production_kwh": "Annual Production (kWh)",
                "specific_yield_kwh_per_kw": "Specific Yield (kWh/kW)",
                "estimated_cost_usd": "Estimated Cost ($)",
                "estimated_LCOE_usd_per_kWh": "LCOE ($/kWh)",
            },
        )

        # --- Final Decision ---
        final_data = result.get("final_decision", {})
        with st.expander("✅ Final Feasibility Decision", expanded=True):
            score = final_data.get("score", 0)
            decision = final_data.get("go_no_go", "N/A")
            st.markdown(f"### Decision: **{decision}** {color_score(score)}", unsafe_allow_html=True)
            st.json(final_data)

        # --- Save Output (optional) ---
        if save_output:
            os.makedirs("outputs", exist_ok=True)
            file_path = f"outputs/output_{address.replace(' ', '_').replace(',', '')}.json"
            with open(file_path, "w") as f:
                json.dump(result, f, indent=2)
            st.success(f"💾 Results saved to `{file_path}`")

    except Exception as e:
        st.error(f"❌ Error running evaluation: {e}")
