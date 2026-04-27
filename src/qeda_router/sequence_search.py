from __future__ import annotations

from .single_side_router import build_route_specs, route_layout, sort_routes_by_boundary_distance


def run_sequence_search(layout: dict) -> dict:
    input_order = [route["route_id"] for route in build_route_specs(layout)]
    candidate_orders = {
        "input_order": input_order,
        "reversed_order": list(reversed(input_order)),
        "boundary_distance_order": sort_routes_by_boundary_distance(layout),
    }

    candidates: list[dict] = []
    for name, order in candidate_orders.items():
        result = route_layout(layout, order)
        result["sequence_name"] = name
        candidates.append(result)

    candidates.sort(
        key=lambda result: (
            -result["success_count"],
            result["total_corners"],
            result["total_wire_length"],
        )
    )
    best = candidates[0]
    return {"best_result": best, "candidates": candidates}

