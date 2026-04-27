from __future__ import annotations

from math import ceil


Point = tuple[int, int]


def manhattan_distance(a: Point, b: Point) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean_like_distance(a: Point, b: Point) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def inflate_rectangle(rect: dict[str, int], margin: int) -> dict[str, int]:
    return {
        "x": rect["x"] - margin,
        "y": rect["y"] - margin,
        "width": rect["width"] + 2 * margin,
        "height": rect["height"] + 2 * margin,
    }


def point_in_rectangle(point: Point, rect: dict[str, int]) -> bool:
    x, y = point
    return (
        rect["x"] <= x <= rect["x"] + rect["width"]
        and rect["y"] <= y <= rect["y"] + rect["height"]
    )


def nearest_enabled_edge_distance(
    point: Point, chip: dict[str, int], escape_edges: dict[str, bool]
) -> int:
    candidates: list[int] = []
    x, y = point
    if escape_edges.get("left"):
        candidates.append(x)
    if escape_edges.get("right"):
        candidates.append(chip["width"] - x)
    if escape_edges.get("bottom"):
        candidates.append(y)
    if escape_edges.get("top"):
        candidates.append(chip["height"] - y)
    return min(candidates) if candidates else 0


def clearance_to_steps(clearance: int, grid_size: int) -> int:
    return ceil(clearance / grid_size)

