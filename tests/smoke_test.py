import asyncio
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.orchestrator import run_many

def test_smoke():
    bundles = asyncio.run(run_many(["123 Solar Way, Phoenix, AZ"]))
    assert len(bundles) == 1
    bundle, final = bundles[0]
    assert bundle.design.capacity_kw >= 0
    assert final.decision in {"GO", "NO-GO"}
