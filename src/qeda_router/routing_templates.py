from __future__ import annotations


def build_simplified_templates(grid_size: int) -> dict[str, list[list[tuple[int, int]]]]:
    """Return small discrete templates used for documentation and debugging."""
    step = grid_size
    return {
        "straight": [
            [(0, 0), (step, 0), (2 * step, 0)],
            [(0, 0), (0, step), (0, 2 * step)],
        ],
        "turn": [
            [(0, 0), (step, 0), (step, step)],
            [(0, 0), (0, step), (step, step)],
        ],
        "offset": [
            [(0, 0), (step, 0), (step, step), (2 * step, step)],
            [(0, 0), (0, step), (step, step), (step, 2 * step)],
        ],
    }

