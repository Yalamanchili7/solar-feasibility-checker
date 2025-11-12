# app/agents/design_agent.py

import os
import json
import requests
from datetime import datetime
from app.utils.llm_client import LLMClient
from app.utils.config import NREL_API_KEY
from app.utils.geocode import geocode_address

LOG_DIR = "outputs/logs/design_agent"
CACHE_DIR = ".cache/design_agent"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


class DesignAgent:
    """
    Design Agent:
    - Geocodes address
    - Calls NREL PVWatts API
    - Uses LLM to summarize solar system performance, design, and cost
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    # -----------------------------
    # STEP 1: Call PVWatts API (with caching + fallback)
    # -----------------------------
    def call_pvwatts(self, lat: float, lon: float, system_capacity_kw: float = 50.0):
        """Call NREL PVWatts API and return structured JSON."""
        cache_path = os.path.join(CACHE_DIR, f"{round(lat, 2)}_{round(lon, 2)}.json")

        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return json.load(f)

        if not NREL_API_KEY:
            print("⚠️ NREL_API_KEY missing — returning static mock data.")
            return {"outputs": {"ac_annual": 75000, "dc_annual": 82000, "capacity": system_capacity_kw}}

        url = "https://developer.nrel.gov/api/pvwatts/v8.json"
        dataset = "tmy3" if 14 < lat < 60 and -170 < lon < -30 else "intl"
        params = {
            "api_key": NREL_API_KEY,
            "lat": lat,
            "lon": lon,
            "system_capacity": system_capacity_kw,
            "azimuth": 180,
            "tilt": 20,
            "array_type": 1,
            "module_type": 1,
            "losses": 14,
            "dataset": dataset,
        }

        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"⚠️ PVWatts request failed: {e}")
            data = {
                "outputs": {
                    "ac_annual": 60000,
                    "dc_annual": 70000,
                    "capacity": system_capacity_kw,
                    "error": str(e),
                }
            }

        # Cache response for reproducibility
        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2)
        return data

    # -----------------------------
    # STEP 2: Analyze system design via LLM
    # -----------------------------
    def analyze_design_with_llm(self, address: str, lat: float, lon: float, pvwatts_data: dict):
        """Use LLM to summarize PV system design, generate BoM, and estimate cost."""
        system_prompt = (
            "You are a senior solar design engineer. "
            "Given PVWatts outputs, produce a detailed system summary with production, cost, "
            "and a Bill of Materials. Respond strictly in JSON — no markdown or prose."
        )

        outputs = pvwatts_data.get("outputs", {})
        user_prompt = f"""
Address: {address}
Location: lat={lat}, lon={lon}

PVWatts outputs:
{json.dumps(outputs, indent=2)}

Instructions:
1. Assume a rooftop system of the given 'system_capacity' in kWdc.
2. Use AC/DC ratio = 1.2 to compute kWac.
3. Estimate annual production using 'ac_annual' or 'dc_annual'.
4. Compute specific_yield_kwh_per_kw = annual_production / system_capacity.
5. Estimate installed cost = 1200 USD per kWdc.
6. Estimate LCOE (Levelized Cost of Energy) = cost / (annual_production_kwh * 25 years).
7. Return valid JSON with:
   - system_capacity_kwdc
   - system_capacity_kwac
   - annual_production_kwh
   - specific_yield_kwh_per_kw
   - estimated_cost_usd
   - estimated_LCOE_usd_per_kWh
   - bill_of_materials:
       - modules: {{"quantity": int, "model": str, "power_w": int}}
       - inverters: {{"quantity": int, "model": str, "capacity_kw": int}}
       - racking: {{"type": str, "material": str}}
       - bos: [list of other components]
   - design_notes: list of 3–5 short insights about efficiency, assumptions, or shading.
Output only valid JSON.
"""

        raw_response = self.llm.chat(system_prompt, user_prompt)

        # Parse or fallback gracefully
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError:
            print("⚠️ Invalid LLM JSON — using fallback.")
            cap = outputs.get("capacity", 50.0)
            prod = outputs.get("ac_annual", 70000)
            parsed = {
                "system_capacity_kwdc": cap,
                "system_capacity_kwac": round(cap / 1.2, 2),
                "annual_production_kwh": prod,
                "specific_yield_kwh_per_kw": round(prod / cap, 2),
                "estimated_cost_usd": round(cap * 1200, 2),
                "estimated_LCOE_usd_per_kWh": round((cap * 1200) / (prod * 25), 3),
                "bill_of_materials": {
                    "modules": {"quantity": 125, "model": "400W Mono", "power_w": 400},
                    "inverters": {"quantity": 5, "model": "10kW string inverter", "capacity_kw": 10},
                    "racking": {"type": "Roof Mount", "material": "Aluminum"},
                    "bos": ["DC Disconnect", "AC Disconnect", "Wiring", "Combiner Box"],
                },
                "design_notes": [
                    "Fallback JSON used due to invalid LLM output.",
                    "Default performance ratios assumed.",
                    "Cost based on $1.2/Wdc industry benchmark.",
                ],
            }

        # Compute simple performance-based score (100 = excellent)
        score = 100
        if parsed.get("specific_yield_kwh_per_kw", 0) < 1000:
            score -= 20
        if parsed.get("estimated_LCOE_usd_per_kWh", 0) > 0.08:
            score -= 15
        parsed["score"] = max(0, min(100, int(score)))

        # Log everything
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
                    "parsed_output": parsed,
                },
                f,
                indent=2,
            )

        return parsed

    # -----------------------------
    # STEP 3: Full run pipeline
    # -----------------------------
    def run(self, address: str):
        """Execute full solar design workflow."""
        print(f"📐 Running DesignAgent for: {address}")
        try:
            lat, lon = geocode_address(address)
            if not lat or not lon:
                raise RuntimeError("Could not geocode address.")

            pv_data = self.call_pvwatts(lat, lon)
            design_data = self.analyze_design_with_llm(address, lat, lon, pv_data)

        except Exception as e:
            print(f"❌ DesignAgent error: {e}")
            design_data = {"error": str(e), "score": 0}
            pv_data = {}

        return {
            "agent": "DesignAgent",
            "address": address,
            "pvwatts_raw": pv_data,
            "design": design_data,
        }
