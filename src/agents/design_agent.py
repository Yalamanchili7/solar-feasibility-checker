import math
import pandas as pd
from ..models import DesignResult
from ..utils.io import read_csv

DEFAULT_PANEL_W = 410  # typical modern solar panel wattage
PR = 0.8  # performance ratio for system losses


class DesignAgent:
    """Simulates basic solar design and energy yield estimation."""

    def __init__(self):
        self.name = "Design"

    def _load_irradiance_data(self):
        """Load the mock solar irradiance dataset."""
        return read_csv("mock_solar_irradiance.csv")

    def _lookup_irradiance(self, city: str, state: str):
        """Return the GHI (kWh/m²/year) for the given city/state, or None if missing."""
        df = self._load_irradiance_data()
        match = df[
            (df["city"].str.lower() == city.lower())
            & (df["state"].str.lower() == state.lower())
        ]
        if not match.empty:
            return float(match.iloc[0]["ghi_kwh_m2_yr"])
        return None  # No data found for this location

    def _generate_bom(self, capacity_kw: float):
        """Generate a simple mock bill of materials."""
        if capacity_kw <= 0:
            return []  # No system = no materials
        num_panels = round(capacity_kw * 1000 / DEFAULT_PANEL_W)
        inverter_kw = round(capacity_kw * 0.83, 1)
        return [
            f"{num_panels}× {DEFAULT_PANEL_W}W panels",
            f"{inverter_kw} kW inverter",
            "Mounting kit",
        ]

    async def run(self, address: str, city: str, state: str, roof_area: float = 80.0):
        """Run design simulation or report if no irradiance data exists."""
        ghi = self._lookup_irradiance(city, state)

        # --- Handle missing data gracefully ---
        if ghi is None:
            return DesignResult(
                address=address,
                capacity_kw=0,
                annual_kwh=0,
                bom=[],
                assumptions={"error": f"No irradiance data available for {city}, {state}"},
            )

        # --- Estimate number of panels and capacity ---
        packing_factor = 0.6  # portion of roof usable for panels
        module_area = 2.0  # m² per module (approx.)
        n_mod = math.floor((roof_area * packing_factor) / module_area)
        dc_kw = round(n_mod * DEFAULT_PANEL_W / 1000, 2)
        annual_kwh = round(dc_kw * ghi * PR, 0)

        bom = self._generate_bom(dc_kw)

        return DesignResult(
            address=address,
            capacity_kw=dc_kw,
            annual_kwh=annual_kwh,
            bom=bom,
            assumptions={
                "ghi_kwh_m2_yr": ghi,
                "performance_ratio": PR,
                "roof_area_m2": roof_area,
                "modules": n_mod,
            },
        )
