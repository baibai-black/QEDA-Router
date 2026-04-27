from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_layout(path: str | Path) -> dict[str, Any]:
    """Load a layout YAML file and return a normalized dictionary."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    normalized, errors, warnings = validate_layout_dict(data)
    if errors:
        joined = "\n".join(errors)
        raise ValueError(f"Invalid layout file {path}:\n{joined}")
    normalized["warnings"] = warnings
    normalized["source_path"] = str(path)
    return normalized


def validate_layout_dict(data: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    """Validate the layout schema used by the demo project."""
    errors: list[str] = []
    warnings: list[str] = []

    chip = data.get("chip", {})
    process = data.get("process", {})
    escape_edges = data.get("escape_edges", {})

    normalized = {
        "chip": {
            "width": _positive_int(chip.get("width"), "chip.width", errors),
            "height": _positive_int(chip.get("height"), "chip.height", errors),
            "grid_size": _positive_int(chip.get("grid_size"), "chip.grid_size", errors),
        },
        "process": {
            "d1": _nonnegative_int(process.get("d1"), "process.d1", errors),
            "d2": _nonnegative_int(process.get("d2"), "process.d2", errors),
            "db": _nonnegative_int(process.get("db"), "process.db", errors),
            "r": _nonnegative_int(process.get("r"), "process.r", errors),
        },
        "escape_edges": {
            "left": bool(escape_edges.get("left", False)),
            "right": bool(escape_edges.get("right", False)),
            "top": bool(escape_edges.get("top", False)),
            "bottom": bool(escape_edges.get("bottom", False)),
        },
        "obstacles": _normalize_obstacles(data.get("obstacles", []), errors),
        "control_starts": _normalize_points(data.get("control_starts", []), "control", errors),
        "readout_starts": _normalize_points(data.get("readout_starts", []), "readout", errors),
    }

    if not any(normalized["escape_edges"].values()):
        errors.append("At least one escape edge must be enabled.")

    if not normalized["control_starts"] and not normalized["readout_starts"]:
        warnings.append("No routes are defined in the layout.")

    if normalized["process"]["r"] > normalized["chip"]["grid_size"]:
        warnings.append(
            "Turning radius r is only approximated on the discrete grid in this demo."
        )

    return normalized, errors, warnings


def _normalize_obstacles(raw_obstacles: Any, errors: list[str]) -> list[dict[str, Any]]:
    obstacles: list[dict[str, Any]] = []
    if raw_obstacles is None:
        return obstacles
    if not isinstance(raw_obstacles, list):
        errors.append("obstacles must be a list.")
        return obstacles

    for index, item in enumerate(raw_obstacles):
        if not isinstance(item, dict):
            errors.append(f"obstacles[{index}] must be a mapping.")
            continue
        if item.get("type") != "rectangle":
            errors.append(f"obstacles[{index}] only supports type=rectangle in the MVP.")
            continue
        obstacle = {
            "name": item.get("name", f"obstacle_{index}"),
            "type": "rectangle",
            "x": _nonnegative_int(item.get("x"), f"obstacles[{index}].x", errors),
            "y": _nonnegative_int(item.get("y"), f"obstacles[{index}].y", errors),
            "width": _positive_int(item.get("width"), f"obstacles[{index}].width", errors),
            "height": _positive_int(item.get("height"), f"obstacles[{index}].height", errors),
        }
        obstacles.append(obstacle)
    return obstacles


def _normalize_points(raw_points: Any, prefix: str, errors: list[str]) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    if raw_points is None:
        return points
    if not isinstance(raw_points, list):
        errors.append(f"{prefix}_starts must be a list.")
        return points

    for index, item in enumerate(raw_points):
        if not isinstance(item, dict):
            errors.append(f"{prefix}_starts[{index}] must be a mapping.")
            continue
        points.append(
            {
                "name": item.get("name", f"{prefix}_{index}"),
                "x": _nonnegative_int(item.get("x"), f"{prefix}_starts[{index}].x", errors),
                "y": _nonnegative_int(item.get("y"), f"{prefix}_starts[{index}].y", errors),
            }
        )
    return points


def _positive_int(value: Any, field: str, errors: list[str]) -> int:
    if not isinstance(value, int) or value <= 0:
        errors.append(f"{field} must be a positive integer.")
        return 0
    return value


def _nonnegative_int(value: Any, field: str, errors: list[str]) -> int:
    if not isinstance(value, int) or value < 0:
        errors.append(f"{field} must be a non-negative integer.")
        return 0
    return value

