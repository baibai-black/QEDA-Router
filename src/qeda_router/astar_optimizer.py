from __future__ import annotations

from copy import deepcopy

from .grid_model import GridModel, expand_cells
from .metrics import route_score
from .single_side_router import build_route_specs, route_single_route


def optimize_routes(layout: dict, solution: dict) -> dict:
    optimized = deepcopy(solution)
    route_lookup = {route["route_id"]: route for route in build_route_specs(layout)}

    for route in optimized["routes"]:
        if not route["success"] or route["escape_edge"] is None:
            continue

        other_occupied = _occupied_cells_for_other_routes(layout, optimized["routes"], route["route_id"])
        grid = GridModel(
            chip_width=layout["chip"]["width"],
            chip_height=layout["chip"]["height"],
            grid_size=layout["chip"]["grid_size"],
        )
        grid.mark_obstacles(layout["obstacles"], layout["process"]["db"])
        rerouted = route_single_route(
            layout=layout,
            grid=grid,
            route=route_lookup[route["route_id"]],
            occupied=other_occupied,
            bend_penalty=9,
            preferred_edge=route["escape_edge"],
        )
        if not rerouted["success"]:
            continue
        if route_score(rerouted["path"]) < route_score(route["path"]):
            rerouted["warnings"].append("Local bend-first A* optimization replaced the original legal path.")
            route.update(rerouted)

    optimized["total_corners"] = sum(route["corner_count"] for route in optimized["routes"] if route["success"])
    optimized["total_wire_length"] = sum(route["path_length"] for route in optimized["routes"] if route["success"])
    return optimized


def _occupied_cells_for_other_routes(layout: dict, routes: list[dict], excluded_route_id: str) -> set[tuple[int, int]]:
    grid = GridModel(
        chip_width=layout["chip"]["width"],
        chip_height=layout["chip"]["height"],
        grid_size=layout["chip"]["grid_size"],
    )
    occupied: set[tuple[int, int]] = set()
    for route in routes:
        if not route["success"] or route["route_id"] == excluded_route_id:
            continue
        route_cells = [grid.world_to_grid(point) for point in route["path"]]
        spacing = layout["process"]["d2"] if route["route_type"] == "readout" else layout["process"]["d1"]
        occupied.update(expand_cells(route_cells, spacing, grid.grid_size))
    return occupied

