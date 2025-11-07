from ..models import PermitChecklistItem, PermitForm, PermittingResult
from ..utils.io import read_json


class PermittingAgent:
    """Simulates local permitting classification and form generation."""

    def __init__(self):
        self.name = "Permitting"

    def _auto_fill_fields(self, project_type: str):
        """Mock logic for auto-filling known permit fields."""
        return {
            "Project Type": project_type,
            "Mounting": "Flush Mount" if "roof" in project_type.lower() else "Ground Mount",
            "Applicant Name": "Feasibility Bot",
            "Contact Email": "demo@example.com",
        }

    def _checklist_for_jurisdiction(self, jurisdiction: str):
        """Look up mock permit requirements for the given jurisdiction."""
        rules = read_json("dummy_permit_rules.json")

        # Try exact match first (e.g., "Tempe, AZ")
        if jurisdiction in rules:
            rule = rules[jurisdiction]
            note = f"Matched permitting data for {jurisdiction}"
        else:
            # Extract just the city part ("Tempe, AZ" -> "Tempe")
            city_only = jurisdiction.split(",")[0].strip()
            rule = rules.get(city_only)

            if rule:
                note = f"Using city-level data for {city_only}"
            else:
                rule = rules.get("DEFAULT")
                note = f"No match found for {jurisdiction}, using DEFAULT permitting checklist"

        # Optional debug note — helps track fallback behavior
        print(f"[PermittingAgent] {note}")

        if not rule:
            return None

        return [PermitChecklistItem(item=i) for i in rule["required_documents"]]

    async def run(self, address: str, jurisdiction: str, project_type: str = "Rooftop Solar"):
        """Run the permitting agent — generate a mock permit form or show missing data."""
        checklist = self._checklist_for_jurisdiction(jurisdiction)

        if checklist is None:
            # No data for this location → mark as low readiness
            return PermittingResult(
                address=address,
                jurisdiction=jurisdiction,
                form=None,
                readiness_score=0,
                blockers=["No permitting data found for this jurisdiction."]
            )

        # Otherwise, build a valid form
        fields = self._auto_fill_fields(project_type)
        form = PermitForm(
            jurisdiction=jurisdiction,
            project_type=project_type,
            auto_filled_fields=fields,
            checklist=checklist,
        )

        return PermittingResult(
            address=address,
            jurisdiction=jurisdiction,
            form=form,
            readiness_score=80,
            blockers=[],
        )
