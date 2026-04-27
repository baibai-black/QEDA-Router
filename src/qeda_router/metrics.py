from __future__ import annotations

from .geometry import Point, manhattan_distance


def path_length(points: list[Point]) -> int:
    if len(points) < 2:
        return 0
    return sum(manhattan_distance(points[index], points[index + 1]) for index in range(len(points) - 1))


def corner_count(points: list[Point]) -> int:
    if len(points) < 3:
        return 0

    corners = 0
    for index in range(1, len(points) - 1):
        previous = points[index - 1]
        current = points[index]
        following = points[index + 1]
        direction_in = (current[0] - previous[0], current[1] - previous[1])
        direction_out = (following[0] - current[0], following[1] - current[1])
        if direction_in != direction_out:
            corners += 1
    return corners


def route_score(points: list[Point]) -> tuple[int, int]:
    return (corner_count(points), path_length(points))

