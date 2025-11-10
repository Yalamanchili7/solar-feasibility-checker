import asyncio
from src.orchestrator import run_many

def test_smoke():
    bundles = asyncio.run(run_many(["123 Solar Way, Phoenix, AZ"]))
    assert len(bundles) == 1

    bundle = bundles[0]
    assert bundle.address == "123 Solar Way, Phoenix, AZ"
    assert bundle.score > 0
    assert bundle.decision in ["GO", "NO-GO", "INVALID"]
