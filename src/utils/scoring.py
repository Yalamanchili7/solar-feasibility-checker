from ..models import AgentBundle

def score_bundle(bundle: AgentBundle) -> int:
    research_points = 40 if bundle.research.favorable_policy else 10
    permitting_points = int(0.3 * bundle.permitting.readiness_score)
    design_ok = bundle.design.capacity_kw >= 3.0 and bundle.design.annual_kwh >= 3000
    design_points = 30 if design_ok else 10
    return min(100, research_points + permitting_points + design_points)

def reasons(bundle: AgentBundle, total: int):
    r = []
    r.append("Policy signals favorable." if bundle.research.favorable_policy else "Unclear or negative policy signals.")
    if bundle.permitting.blockers:
        r.extend([f"Permitting blocker: {b}" for b in bundle.permitting.blockers])
    else:
        r.append("Permitting looks feasible with standard docs.")
    r.append("Design capacity acceptable." if bundle.design.capacity_kw >= 3 else "Design capacity < 3 kW.")
    r.append(f"Composite score: {total}")
    return r
