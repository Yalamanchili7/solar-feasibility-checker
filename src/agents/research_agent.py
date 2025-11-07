import asyncio
from ..models import ResearchResult, ResearchFinding
from ..utils.io import read_json

class ResearchAgent:
    """Simulates policy and permitting research using local dummy data."""

    def __init__(self):
        self.name = "Research"
        self.data_path = "dummy_policy_data.json"

    async def run(self, address: str, city: str, state: str) -> ResearchResult:
        """Lookup the location in dummy policy data and return a simulated result."""
        await asyncio.sleep(0.2)  # simulate small API delay
        policies = read_json(self.data_path)
        key = f"{city}, {state}"

        if key in policies:
            entry = policies[key]
        else:
            entry = policies["DEFAULT"]

        sentiment = entry["sentiment"]
        headlines = entry["headlines"]

        # Convert to ResearchFinding list
        findings = [
            ResearchFinding(source="dummy", title=h, sentiment=sentiment)
            for h in headlines
        ]

        # Build rationale + favorable flag
        if sentiment == "positive":
            rationale = f"{city}, {state} shows favorable policy signals for solar deployment."
            favorable = True
        elif sentiment == "neutral":
            rationale = f"{city}, {state} shows no clear policy signals — assuming neutral environment."
            favorable = False
        else:  # negative
            rationale = f"{city}, {state} shows restrictive or uncertain solar policy trends."
            favorable = False

        return ResearchResult(
            address=address,
            favorable_policy=favorable,
            rationale=rationale,
            findings=findings,
        )
