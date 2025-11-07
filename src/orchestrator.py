# src/orchestrator.py

import asyncio
from typing import List
from src.utils.geo import parse_jurisdiction_from_address
from src.agents.research_agent import ResearchAgent
from src.agents.permitting_agent import PermittingAgent
from src.agents.design_agent import DesignAgent
from src.models import SiteBundle


async def run_for_address(address: str) -> SiteBundle:
    """
    Runs all agents for a single address, computes weighted feasibility scores,
    and generates a transparent summary explaining how the decision was reached.
    """

    # --- Step 1: Validate address format ---
    try:
        city, state, _ = parse_jurisdiction_from_address(address)
    except ValueError:
        return SiteBundle(
            address=address,
            score=0,
            decision="INVALID",
            summary=f"Invalid address format: '{address}'. Please use '123 Main St, City, ST'.",
            results=[],
        )

    # --- Step 2: Initialize all agents ---
    research_agent = ResearchAgent()
    permitting_agent = PermittingAgent()
    design_agent = DesignAgent()

    # --- Step 3: Run agents concurrently ---
    research_result, permit_result, design_result = await asyncio.gather(
        research_agent.run(address, city, state),
        permitting_agent.run(address, f"{city}, {state}"),
        design_agent.run(address, city, state),
    )

    # --- Step 4: Compute scores ---

    # Research: Favorable policy environment
    if not research_result.favorable_policy:
        if "No reliable policy data" in research_result.rationale:
            research_score = 20  # heavy penalty for missing data
        else:
            research_score = 40  # unfavorable signals
    else:
        research_score = 90  # favorable signals

    # Permitting: Readiness of jurisdiction
    if not permit_result.form or permit_result.readiness_score == 0:
        permit_score = 0  # no data means no score
    else:
        permit_score = permit_result.readiness_score

    # Design: Technical feasibility
    if design_result.capacity_kw == 0:
        design_score = 20  # missing or low irradiance data
    else:
        design_score = min(design_result.capacity_kw * 10, 100)


    # --- Step 5: Weighted composite score ---
    weights = {"research": 0.4, "permitting": 0.3, "design": 0.3}
    composite_score = round(
        research_score * weights["research"]
        + permit_score * weights["permitting"]
        + design_score * weights["design"],
        1,
    )

    decision = "GO" if composite_score >= 70 else "NO-GO"

    # --- Step 6: Score breakdown for transparency ---
    score_breakdown = (
        f"\nFeasibility Score Breakdown:\n"
        f"• Research Score: {research_score}/100\n"
        f"• Permitting Score: {permit_score}/100\n"
        f"• Design Score: {design_score}/100\n"
        f"• Weighted Composite: {composite_score}/100\n"
    )

    # --- Step 7: Build summary ---
    bom_items = ", ".join(design_result.bom) if design_result.bom else "No BoM available"

    summary_lines = [
        f"Research → {research_result.rationale}",
        (
            f"Permitting → {permit_result.jurisdiction} ({permit_result.readiness_score}/100)"
            if permit_result.readiness_score > 0
            else f"Permitting → No permitting data found for {permit_result.jurisdiction}."
        ),
        f"Design → {design_result.capacity_kw} kW → {design_result.annual_kwh} kWh/yr",
        f"BoM → {bom_items}",
        score_breakdown.strip(),  # add breakdown visibly
    ]

    # --- Step 8: Add rationale if missing data caused penalty ---
    if composite_score < 70 and (
        "No reliable policy data" in research_result.rationale
        or not permit_result.form
        or not design_result.bom
    ):
        summary_lines.insert(0, "⚠️ Limited or missing data reduced feasibility confidence.")

    # Join all text lines
    summary = "\n".join(summary_lines)

    # --- Step 9: Return unified bundle for this address ---
    return SiteBundle(
        address=address,
        score=composite_score,
        decision=decision,
        summary=summary,
        results=[
            research_result.model_dump(),
            permit_result.model_dump(),
            design_result.model_dump(),
        ],
    )


async def run_many(addresses: List[str]) -> List[SiteBundle]:
    """Run the multi-agent pipeline for multiple addresses concurrently."""
    return await asyncio.gather(*[run_for_address(addr) for addr in addresses]) 
