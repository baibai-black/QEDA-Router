from __future__ import annotations

from dataclasses import dataclass, field

from .geometry import Point, clearance_to_steps, inflate_rectangle, point_in_rectangle


@dataclass
class GridModel:
    chip_width: int
    chip_height: int
    grid_size: int
    obstacle_blocked: set[Point] = field(default_factory=set)

    @property
    def nx(self) -> int:
        return self.chip_width // self.grid_size + 1

    @property
    def ny(self) -> int:
        return self.chip_height // self.grid_size + 1

    def world_to_grid(self, point: Point) -> Point:
        return (round(point[0] / self.grid_size), round(point[1] / self.grid_size))

    def grid_to_world(self, point: Point) -> Point:
        return (point[0] * self.grid_size, point[1] * self.grid_size)

    def in_bounds(self, point: Point) -> bool:
        return 0 <= point[0] < self.nx and 0 <= point[1] < self.ny

    def neighbors(self, point: Point) -> list[Point]:
        candidates = [
            (point[0] + 1, point[1]),
            (point[0] - 1, point[1]),
            (point[0], point[1] + 1),
            (point[0], point[1] - 1),
        ]
        return [candidate for candidate in candidates if self.in_bounds(candidate)]

    def mark_obstacles(self, obstacles: list[dict[str, int]], clearance: int) -> None:
        for obstacle in obstacles:
            inflated = inflate_rectangle(obstacle, clearance)
            for gx in range(self.nx):
                for gy in range(self.ny):
                    world_point = self.grid_to_world((gx, gy))
                    if point_in_rectangle(world_point, inflated):
                        self.obstacle_blocked.add((gx, gy))

    def boundary_cells(self, enabled_edges: dict[str, bool]) -> dict[str, list[Point]]:
        boundaries: dict[str, list[Point]] = {"left": [], "right": [], "top": [], "bottom": []}
        for gy in range(self.ny):
            boundaries["left"].append((0, gy))
            boundaries["right"].append((self.nx - 1, gy))
        for gx in range(self.nx):
            boundaries["bottom"].append((gx, 0))
            boundaries["top"].append((gx, self.ny - 1))
        return {
            edge: cells
            for edge, cells in boundaries.items()
            if enabled_edges.get(edge, False)
        }


def expand_cells(cells: list[Point] | set[Point], clearance: int, grid_size: int) -> set[Point]:
    step_margin = clearance_to_steps(clearance, grid_size)
    expanded: set[Point] = set()
    for x, y in cells:
        for dx in range(-step_margin, step_margin + 1):
            for dy in range(-step_margin, step_margin + 1):
                expanded.add((x + dx, y + dy))
    return expanded

