from __future__ import annotations

from pathlib import Path

import typer

from .astar_optimizer import optimize_routes
from .config_loader import load_layout, validate_layout_dict
from .drc import run_basic_drc
from .report_writer import write_outputs
from .sequence_search import run_sequence_search
from .visualizer import draw_layout_preview

app = typer.Typer(help="QEDA-Router: a learning/demo CLI for simplified quantum chip escape routing.")


@app.command()
def validate(layout: Path = typer.Option(..., exists=True, dir_okay=False, help="Path to layout.yaml")) -> None:
    """Validate a toy layout file and print summary information."""
    with layout.open("r", encoding="utf-8") as handle:
        import yaml

        raw = yaml.safe_load(handle) or {}
    normalized, errors, warnings = validate_layout_dict(raw)

    if errors:
        for error in errors:
            typer.echo(f"ERROR: {error}")
        raise typer.Exit(code=1)

    typer.echo("Layout validation passed.")
    typer.echo(
        f"Chip: {normalized['chip']['width']} x {normalized['chip']['height']} | "
        f"grid_size={normalized['chip']['grid_size']}"
    )
    typer.echo(
        f"Routes: control={len(normalized['control_starts'])}, "
        f"readout={len(normalized['readout_starts'])}, obstacles={len(normalized['obstacles'])}"
    )
    if warnings:
        typer.echo("Warnings:")
        for warning in warnings:
            typer.echo(f"- {warning}")


@app.command()
def route(
    layout: Path = typer.Option(..., exists=True, dir_okay=False, help="Path to layout.yaml"),
    out: Path = typer.Option(..., help="Output directory"),
) -> None:
    """Run the three-stage demo routing flow and write outputs."""
    loaded = load_layout(layout)
    sequence_search = run_sequence_search(loaded)
    best_result = optimize_routes(loaded, sequence_search["best_result"])
    best_result["sequence_name"] = sequence_search["best_result"]["sequence_name"]
    drc_report = run_basic_drc(loaded, best_result["routes"])
    output_paths = write_outputs(loaded, best_result, drc_report, out)
    draw_layout_preview(loaded, best_result["routes"], out / "layout_preview.png")

    typer.echo(f"Routing finished. Success rate: {best_result['success_rate']:.2%}")
    typer.echo(f"Chosen sequence: {best_result['sequence_name']}")
    typer.echo(f"Summary CSV: {output_paths['summary_csv']}")


@app.command()
def demo(out: Path = typer.Option(..., help="Output directory for the bundled toy demo")) -> None:
    """Run the bundled 4-qubit toy example."""
    project_root = Path(__file__).resolve().parents[2]
    layout = project_root / "examples" / "4qubit" / "layout.yaml"
    route(layout=layout, out=out)


if __name__ == "__main__":
    app()

