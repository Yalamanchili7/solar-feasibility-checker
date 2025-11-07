import json
import asyncio
import click
from pathlib import Path
from rich import print
from rich.panel import Panel
from rich.table import Table
from src.orchestrator import run_many
from src.utils.io import write_json


@click.command()
@click.option(
    "--address",
    required=True,
    help="Enter a full address (e.g. '123 Main St, City, ST').",
)
@click.option(
    "--out",
    type=click.Path(path_type=Path),
    default=Path("outputs"),
    help="Directory where the JSON report will be saved.",
)
def main(address: str, out: Path):
    """Run the Solar Feasibility multi-agent system for a single address."""
    out.mkdir(parents=True, exist_ok=True)

    print("\n[bold green]🔆 Running Solar Feasibility Check...[/bold green]\n")

    # Run orchestrator
    results = asyncio.run(run_many([address.strip()]))
    bundle = results[0]  # single address mode

    # Save JSON output
    safe_name = bundle.address.replace(" ", "_").replace(",", "")
    json_path = out / f"{safe_name}.json"
    write_json(json_path, bundle.model_dump())

    # --- Display header ---
    header = (
        f"[bold]Address:[/bold] {bundle.address}\n"
        f"[bold]Decision:[/bold] {bundle.decision} ({bundle.score})"
    )
    print(Panel(header, title="Result", expand=False))

    # --- Build summary table ---
    table = Table(title="Agent Summary", show_lines=True)
    table.add_column("Agent", style="bold cyan")
    table.add_column("Summary", style="white")

    for line in bundle.summary.split("\n"):
        if line.startswith("Research"):
            table.add_row("Research", line.replace("Research → ", ""))
        elif line.startswith("Permitting"):
            table.add_row("Permitting", line.replace("Permitting → ", ""))
        elif line.startswith("Design"):
            table.add_row("Design", line.replace("Design → ", ""))
        elif line.startswith("BoM") and bundle.decision == "GO":
            table.add_row("Bill of Materials", line.replace("BoM → ", ""))

    print(table)

    # --- Decision summary ---
    if bundle.decision == "GO":
        print("[green]✅ Site looks feasible for solar installation![/green]")
    elif bundle.decision == "NO-GO":
        print("[yellow]⚠️ Site may not be suitable based on current analysis.[/yellow]")
    else:
        print("[red]❌ Invalid or incomplete address.[/red]")

    print(f"[dim]JSON report saved to:[/dim] {json_path}\n")


if __name__ == "__main__":
    main()
