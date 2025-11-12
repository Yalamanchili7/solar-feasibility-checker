# cli.py
import argparse
import json
import os
import re
from app.utils.llm_client import LLMClient
from app.orchestrator.coordinator import Orchestrator


# ---------------- Utility helpers ---------------- #

def parse_json_block(raw):
    """Cleans markdown fences and parses JSON safely."""
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str):
        return {"raw": str(raw)}
    clean = re.sub(r"```(?:json)?", "", raw, flags=re.IGNORECASE).strip("` \n")
    try:
        return json.loads(clean)
    except Exception:
        return {"raw": clean}


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("-" * 60)


def humanize_research(data):
    print(f"Summary: {data.get('summary', 'N/A')}")
    risks = data.get("risks", [])
    print(f"Risks: {', '.join(risks) if risks else 'None'}")
    print(f"Policy Favorability Score: {data.get('score', 'N/A')}")
    print(f"Sentiment: {data.get('sentiment', 'N/A')}")


def humanize_permitting(data):
    print(f"Jurisdiction: {data.get('jurisdiction', 'N/A')}")
    permits = data.get("permit_required", [])
    print(f"Required Permits: {', '.join(permits) if permits else 'None'}")
    avg_days = data.get("average_review_days", data.get("avg_review_days", 'N/A'))
    print(f"Avg Review Time (days): {avg_days}")
    print(f"Fire Code Setback (inches): {data.get('fire_code_setback_inches', 'N/A')}")
    print(f"Notes: {data.get('special_considerations', 'N/A')}")


def humanize_design(data):
    print(f"System Capacity (kWdc): {data.get('system_capacity_kwdc', 'N/A')}")
    print(f"Annual Production (kWh): {data.get('annual_production_kwh', 'N/A')}")
    print(f"Specific Yield (kWh/kW): {data.get('specific_yield_kwh_per_kw', 'N/A')}")
    bom = data.get("bill_of_materials", {})
    if bom:
        print("Bill of Materials:")
        for key, val in bom.items():
            if isinstance(val, dict):
                val_str = ", ".join(f"{k}: {v}" for k, v in val.items())
                print(f"  - {key}: {val_str}")
            else:
                print(f"  - {key}: {val}")
    notes = data.get("design_notes", [])
    print(f"Notes: {', '.join(notes) if notes else 'N/A'}")


def humanize_final(data):
    print(f"Decision: {data.get('go_no_go', 'N/A')}")
    print(f"Score: {data.get('score', 'N/A')}")
    comp = data.get("component_scores", {})
    if comp:
        print("Component Scores:")
        for k, v in comp.items():
            print(f"  - {k.title()}: {v}")
    justifications = data.get("justification", [])
    if justifications:
        print("Justification:")
        for j in justifications:
            print(f"  - {j}")


# ---------------- Main CLI logic ---------------- #

def main():
    parser = argparse.ArgumentParser(
        description="🏗️ Solar Feasibility Checker — Multi-Agent LLM System"
    )
    parser.add_argument(
        "--address",
        type=str,
        required=True,
        help="Enter a valid site address (e.g., 'Austin, Texas' or '123 Main St, San Diego, CA').",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Optionally save full agent outputs to a JSON file inside /outputs folder."
    )

    args = parser.parse_args()
    address = args.address

    print(f"\n🌞 Running Solar Feasibility Analysis for: {address}\n")

    try:
        # ✅ Gracefully handle missing or invalid API keys
        llm = LLMClient()
        orchestrator = Orchestrator(llm)
        result = orchestrator.evaluate_address(address)

        # --- Research Agent ---
        print_section("🔍 RESEARCH AGENT SUMMARY")
        research_data = parse_json_block(result.get("research", {}).get("analysis", {}))
        humanize_research(research_data)

        # --- Permitting Agent ---
        print_section("🏗️ PERMITTING AGENT SUMMARY")
        permit_data = parse_json_block(result.get("permitting", {}).get("permit_form", {}))
        humanize_permitting(permit_data)

        # --- Design Agent ---
        print_section("📐 DESIGN AGENT SUMMARY")
        design_data = parse_json_block(result.get("design", {}).get("design", {}))
        humanize_design(design_data)

        # --- Final Decision ---
        print_section("✅ FINAL DECISION")
        final_data = result.get("final_decision", {})  # structured JSON
        humanize_final(final_data)
        print("=" * 60)

        # --- Save Output ---
        if args.save:
            os.makedirs("outputs", exist_ok=True)
            file_name = f"outputs/output_{address.replace(' ', '_').replace(',', '')}.json"
            with open(file_name, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to: {file_name}")

    except EnvironmentError as e:
        print(f"⚠️ Missing or invalid API key: {e}")
    except Exception as e:
        print(f"❌ Error running evaluation: {e}")

