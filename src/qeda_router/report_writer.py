from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .routing_templates import build_simplified_templates


def write_outputs(layout: dict, sequence_result: dict, drc_report: dict, output_dir: str | Path) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_frame = pd.DataFrame(
        [
            {
                "route_id": route["route_id"],
                "route_type": route["route_type"],
                "success": route["success"],
                "escape_edge": route["escape_edge"],
                "path_length": route["path_length"],
                "corner_count": route["corner_count"],
                "num_points": route["num_points"],
                "warnings": " | ".join(route["warnings"]),
            }
            for route in sequence_result["routes"]
        ]
    )
    summary_path = output_dir / "route_summary.csv"
    summary_frame.to_csv(summary_path, index=False)

    routed_layout = {
        "input_summary": {
            "source_path": layout.get("source_path"),
            "chip": layout["chip"],
            "process": layout["process"],
            "num_control_routes": len(layout["control_starts"]),
            "num_readout_routes": len(layout["readout_starts"]),
            "num_obstacles": len(layout["obstacles"]),
        },
        "modeling_summary": {
            "grid_size": layout["chip"]["grid_size"],
            "template_model": "simplified discrete template model",
            "templates": build_simplified_templates(layout["chip"]["grid_size"]),
        },
        "routing_summary": sequence_result,
    }
    json_path = output_dir / "routed_layout.json"
    json_path.write_text(json.dumps(routed_layout, indent=2), encoding="utf-8")

    drc_path = output_dir / "drc_report.json"
    drc_path.write_text(json.dumps(drc_report, indent=2), encoding="utf-8")

    report_path = output_dir / "report.md"
    report_path.write_text(_build_report_text(layout, sequence_result, drc_report), encoding="utf-8")

    return {
        "summary_csv": summary_path,
        "routed_layout_json": json_path,
        "drc_report_json": drc_path,
        "report_md": report_path,
    }


def _build_report_text(layout: dict, result: dict, drc_report: dict) -> str:
    failed_routes = [route["route_id"] for route in result["routes"] if not route["success"]]
    warning_lines = [f"- {item['message']}" for item in drc_report["warnings"]]
    failed_route_lines = [f"- {route_id}" for route_id in failed_routes] or ["- none"]
    planned_lines = [
        "- accurate curved CPW geometry",
        "- full combination routing template geometry",
        "- tree-search line ordering",
        "- blocking table",
        "- route-swap operation for readout lines",
        "- spatially constrained iterative optimization",
        "- lazy open set",
        "- multi-layer routing",
        "- GDS export",
        "- KLayout integration",
        "- Qiskit Metal/KQCircuits integration",
    ]

    return "\n".join(
        [
            "# QEDA-Router Report",
            "",
            "## Input Summary",
            f"- source: `{layout.get('source_path', 'in-memory layout')}`",
            f"- chip size: {layout['chip']['width']} x {layout['chip']['height']}",
            f"- grid size: {layout['chip']['grid_size']}",
            f"- obstacles: {len(layout['obstacles'])}",
            f"- control routes: {len(layout['control_starts'])}",
            f"- readout routes: {len(layout['readout_starts'])}",
            "",
            "## Modeling Summary",
            "- fine-grid occupancy model built from toy YAML input",
            "- simplified template model includes straight / turn / offset patterns",
            "- curved CPW geometry is not modeled in this MVP",
            "",
            "## Routing Sequence Used",
            f"- sequence: `{result.get('sequence_name', 'unknown')}`",
            f"- order: {', '.join(result['route_order'])}",
            "",
            "## Legal Route Success Rate",
            f"- success count: {result['success_count']} / {result['route_count']}",
            f"- success rate: {result['success_rate']:.2%}",
            "",
            "## Total CoC",
            f"- total corners: {result['total_corners']}",
            "",
            "## Total TWL",
            f"- total wire length: {result['total_wire_length']}",
            "",
            "## DRC Warnings",
            *(warning_lines or ["- none"]),
            "",
            "## Failed Routes",
            *failed_route_lines,
            "",
            "## Planned Limitations",
            *planned_lines,
            "",
            "## Warnings",
            "- This is a learning/demo project and is not suitable for real chip tape-out.",
            "- Successful routing here does not prove physical manufacturability.",
            "- Human review is required for geometry, rule interpretation, and route quality.",
        ]
    )
