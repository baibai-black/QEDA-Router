from __future__ import annotations

from .geometry import euclidean_like_distance, inflate_rectangle, point_in_rectangle


def run_basic_drc(layout: dict, routes: list[dict]) -> dict:
    warnings: list[dict] = []
    per_route: dict[str, list[str]] = {}
    successful_routes = [route for route in routes if route["success"]]

    for route in successful_routes:
        route_warnings = _route_warnings(layout, route)
        per_route[route["route_id"]] = route_warnings
        for message in route_warnings:
            warnings.append({"route_id": route["route_id"], "type": "route_warning", "message": message})

    for index, first in enumerate(successful_routes):
        for second in successful_routes[index + 1 :]:
            message = _spacing_warning(layout, first, second)
            if message:
                warnings.append(
                    {
                        "route_id": f"{first['route_id']}|{second['route_id']}",
                        "type": "spacing_warning",
                        "message": message,
                    }
                )

    warnings.append(
        {
            "route_id": "global",
            "type": "model_warning",
            "message": "DRC is simplified and grid-based; it is not a tape-out signoff deck.",
        }
    )
    return {"warnings": warnings, "per_route": per_route, "warning_count": len(warnings)}


def _route_warnings(layout: dict, route: dict) -> list[str]:
    chip = layout["chip"]
    process = layout["process"]
    messages: list[str] = []

    for point in route["path"]:
        if not (0 <= point[0] <= chip["width"] and 0 <= point[1] <= chip["height"]):
            messages.append("Route contains out-of-bound points.")
            break

    for obstacle in layout["obstacles"]:
        inflated = inflate_rectangle(obstacle, process["db"])
        if any(point_in_rectangle(point, inflated) for point in route["path"]):
            messages.append(f"Route enters obstacle keep-out region around {obstacle['name']}.")
            break

    if route["corner_count"] > 0 and process["r"] > chip["grid_size"]:
        messages.append("Corner radius was not validated against a true curved geometry model.")
    return messages


def _spacing_warning(layout: dict, first: dict, second: dict) -> str | None:
    required = layout["process"]["d2"] if "readout" in {first["route_type"], second["route_type"]} else layout["process"]["d1"]
    for point_a in first["path"]:
        for point_b in second["path"]:
            if euclidean_like_distance(point_a, point_b) < required:
                return (
                    f"Spacing between {first['route_id']} and {second['route_id']} is below the "
                    f"simplified requirement of {required}."
                )
    return None

