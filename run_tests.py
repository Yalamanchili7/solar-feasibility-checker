# run_tests.py
"""
Batch test runner for the Solar Feasibility Checker multi-agent system.
Runs multiple addresses sequentially and saves full results as JSON.
"""

import os
import json
import time
from datetime import datetime
from app.utils.llm_client import LLMClient
from app.orchestrator.coordinator import Orchestrator


# 🧪 Define test addresses
TEST_ADDRESSES = [
    "Austin, TX",
    "Los Angeles, CA",
    "Seattle, WA",
    "Phoenix, AZ",
    "Napa County, CA",
    "Berlin, Germany"
]


def run_tests():
    llm = LLMClient()
    orchestrator = Orchestrator(llm)
    results_summary = []

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = f"test_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n🚀 Running batch feasibility tests for {len(TEST_ADDRESSES)} locations\n")

    for addr in TEST_ADDRESSES:
        print(f"🧠 Evaluating: {addr}")
        try:
            result = orchestrator.evaluate_address(addr)
            score = result["final_decision"].get("score", "N/A")
            decision = result["final_decision"].get("go_no_go", "N/A")

            # Save JSON per address
            file_name = f"{output_dir}/{addr.replace(',', '').replace(' ', '_')}.json"
            with open(file_name, "w") as f:
                json.dump(result, f, indent=2)

            results_summary.append({
                "address": addr,
                "score": score,
                "decision": decision
            })

            print(f"   ✅ Completed — Score: {score}, Decision: {decision}")
        except Exception as e:
            print(f"   ❌ Error processing {addr}: {e}")
        time.sleep(3)  # avoid hitting rate limits between API calls

    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    for item in results_summary:
        print(f"{item['address']:<25} | Score: {item['score']:<5} | Decision: {item['decision']}")
    print("=" * 60)
    print(f"All detailed results saved to: {output_dir}\n")


if __name__ == "__main__":
    run_tests()
