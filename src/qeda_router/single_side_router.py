from __future__ import annotations

import heapq
from copy import deepcopy

from .geometry import Point, nearest_enabled_edge_distance
from .grid_model import GridModel, expand_cells
from .metrics import corner_count, path_length


def build_route_specs(layout: dict) -> list[dict]:
    routes: list[dict] = []
    for item in layout["control_starts"]:
        routes.append({"route_id": item["name"], "route_type": "control", "start": (item["x"], item["y"])})
    for item in layout["readout_starts"]:
        routes.append({"route_id": item["name"], "route_type": "readout", "start": (item["x"], item["y"])})
    return routes


def route_layout(layout: dict, route_order: list[str], bend_penalty: int = 6) -> dict:
    grid = GridModel(
        chip_width=layout["chip"]["width"],
        chip_height=layout["chip"]["height"],
        grid_size=layout["chip"]["grid_size"],
    )
    grid.mark_obstacles(layout["obstacles"], layout["process"]["db"])
    routes_by_id = {route["route_id"]: route for route in build_route_specs(layout)}

    occupied: set[Point] = set()
    results: list[dict] = []
    for route_id in route_order:
        route = routes_by_id[route_id]
        result = route_single_route(
            layout=layout,
            grid=grid,
            route=route,
            occupied=occupied,
            bend_penalty=bend_penalty,
        )
        results.append(result)
        if result["success"]:
            route_cells = [grid.world_to_grid(point) for point in result["path"]]
            occupied.update(expand_cells(route_cells, _spacing_for_route(route["route_type"], layout["process"]), grid.grid_size))

    return _finalize_solution(layout, results, route_order)


def route_single_route(
    layout: dict,
    grid: GridModel,
    route: dict,
    occupied: set[Point],
    bend_penalty: int,
    preferred_edge: str | None = None,
) -> dict:
    start_idx = grid.world_to_grid(route["start"])
    blocked = {cell for cell in occupied if grid.in_bounds(cell)} | grid.obstacle_blocked
    blocked.discard(start_idx)

    allowed_edges = layout["escape_edges"].copy()
    if preferred_edge is not None:
        allowed_edges = {edge: edge == preferred_edge for edge in allowed_edges}

    targets_by_edge = grid.boundary_cells(allowed_edges)
    targets = {
        edge: [cell for cell in cells if cell not in blocked or cell == start_idx]
        for edge, cells in targets_by_edge.items()
    }
    all_targets = {cell for cells in targets.values() for cell in cells}

    if not all_targets:
        return _failed_route(route, ["No reachable escape boundary cells are available."])

    path_cells = _astar_search(grid, start_idx, all_targets, blocked, bend_penalty)
    if path_cells is None:
        return _failed_route(
            route,
            [
                "No legal route found under the current sequence and simplified grid rules.",
                "Result is a demo warning, not a proof that routing is impossible.",
            ],
        )

    world_points = [grid.grid_to_world(cell) for cell in path_cells]
    escape_edge = _detect_escape_edge(path_cells[-1], grid)
    warnings = ["Simplified discrete routing model used; geometry is not fabrication-ready."]
    if corner_count(world_points) > 0 and layout["process"]["r"] > layout["chip"]["grid_size"]:
        warnings.append("Turning radius is approximated on-grid and was not checked with true curved geometry.")

    return {
        "route_id": route["route_id"],
        "route_type": route["route_type"],
        "success": True,
        "escape_edge": escape_edge,
        "path": world_points,
        "path_length": path_length(world_points),
        "corner_count": corner_count(world_points),
        "num_points": len(world_points),
        "warnings": warnings,
    }


def _astar_search(
    grid: GridModel,
    start: Point,
    targets: set[Point],
    blocked: set[Point],
    bend_penalty: int,
) -> list[Point] | None:
    def heuristic(point: Point) -> int:
        return min(abs(point[0] - tx) + abs(point[1] - ty) for tx, ty in targets)

    queue: list[tuple[int, int, Point, Point | None]] = []
    heapq.heappush(queue, (heuristic(start), 0, start, None))

    best_cost: dict[tuple[Point, Point | None], int] = {(start, None): 0}
    previous: dict[tuple[Point, Point | None], tuple[Point, Point | None] | None] = {(start, None): None}

    while queue:
        _, current_cost, current, previous_direction = heapq.heappop(queue)
        if current in targets:
            return _reconstruct_path(previous, (current, previous_direction))

        for neighbor in grid.neighbors(current):
            if neighbor in blocked and neighbor not in targets:
                continue

            direction = (neighbor[0] - current[0], neighbor[1] - current[1])
            turn_cost = bend_penalty if previous_direction and direction != previous_direction else 0
            next_cost = current_cost + 1 + turn_cost
            state = (neighbor, direction)

            if next_cost >= best_cost.get(state, 10**18):
                continue

            best_cost[state] = next_cost
            previous[state] = (current, previous_direction)
            priority = next_cost + heuristic(neighbor)
            heapq.heappush(queue, (priority, next_cost, neighbor, direction))

    return None


def _reconstruct_path(
    previous: dict[tuple[Point, Point | None], tuple[Point, Point | None] | None],
    state: tuple[Point, Point | None],
) -> list[Point]:
    path: list[Point] = []
    cursor: tuple[Point, Point | None] | None = state
    while cursor is not None:
        path.append(cursor[0])
        cursor = previous[cursor]
    path.reverse()
    return path


def _failed_route(route: dict, warnings: list[str]) -> dict:
    return {
        "route_id": route["route_id"],
        "route_type": route["route_type"],
        "success": False,
        "escape_edge": None,
        "path": [],
        "path_length": 0,
        "corner_count": 0,
        "num_points": 0,
        "warnings": warnings,
    }


def _detect_escape_edge(cell: Point, grid: GridModel) -> str:
    if cell[0] == 0:
        return "left"
    if cell[0] == grid.nx - 1:
        return "right"
    if cell[1] == 0:
        return "bottom"
    return "top"


def _spacing_for_route(route_type: str, process: dict) -> int:
    return process["d2"] if route_type == "readout" else process["d1"]


def _finalize_solution(layout: dict, routes: list[dict], route_order: list[str]) -> dict:
    success_count = sum(1 for route in routes if route["success"])
    return {
        "route_order": route_order,
        "routes": routes,
        "success_count": success_count,
        "route_count": len(routes),
        "success_rate": success_count / len(routes) if routes else 0.0,
        "total_corners": sum(route["corner_count"] for route in routes if route["success"]),
        "total_wire_length": sum(route["path_length"] for route in routes if route["success"]),
        "global_warnings": deepcopy(layout.get("warnings", [])),
    }


def sort_routes_by_boundary_distance(layout: dict) -> list[str]:
    specs = build_route_specs(layout)
    specs.sort(
        key=lambda route: nearest_enabled_edge_distance(
            route["start"], layout["chip"], layout["escape_edges"]
        )
    )
    return [route["route_id"] for route in specs]

