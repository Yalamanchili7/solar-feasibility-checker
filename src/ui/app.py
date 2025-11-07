import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import asyncio
from src.orchestrator import run_many


# --- Page Setup ---
st.set_page_config(page_title="Solar Feasibility Checker", page_icon="☀️")
st.title("☀️ Solar Feasibility Checker")
st.write("Enter a full address in the format: `123 Main St, City, ST`")

# --- Input ---
address = st.text_input("Full Address:")

# --- Run Button ---
if st.button("Run Feasibility Check"):
    if not address.strip():
        st.warning("Please enter a valid address before running the check.")
    else:
        try:
            bundles = asyncio.run(run_many([address.strip()]))
            bundle = bundles[0]

            # Handle invalid/error cases
            if bundle.decision == "INVALID":
                st.error(bundle.summary)
                st.stop()
            if bundle.decision == "ERROR":
                st.error(bundle.summary)
                st.stop()

            # --- Decision display ---
            if bundle.decision == "GO":
                st.success(f"✅ {bundle.address}: {bundle.decision} ({bundle.score:.1f})")
            elif bundle.decision == "NO-GO":
                st.warning(f"⚠️ {bundle.address}: {bundle.decision} ({bundle.score:.1f})")
            else:
                st.error(f"❌ {bundle.address}: {bundle.decision} ({bundle.score:.1f})")

            # --- Agent summaries ---
            st.markdown("### Agent Summary")
            for line in bundle.summary.split("\n"):
                if line.startswith("Research"):
                    st.markdown(f"**🧭 {line}**")
                elif line.startswith("Permitting"):
                    st.markdown(f"**📋 {line}**")
                elif line.startswith("Design"):
                    st.markdown(f"**⚙️ {line}**")
                elif line.startswith("BoM") and bundle.decision == "GO":
                    st.markdown("**🔧 Bill of Materials:**")
                    items = line.replace("BoM →", "").split(",")
                    for item in items:
                        clean_item = item.strip()
                        if clean_item:
                            st.markdown(f"- {clean_item}")

            # --- Friendly summary ---
            if bundle.decision == "GO":
                st.success("✅ Site looks feasible for solar installation!")
            elif bundle.decision == "NO-GO":
                st.warning("⚠️ Site may not be suitable based on current analysis.")
            else:
                st.error("❌ Invalid or incomplete address.")

        except Exception as e:
            st.error(f"Something went wrong: {e}")
