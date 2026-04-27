from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def draw_layout_preview(layout: dict, routes: list[dict], output_path: str | Path) -> None:
    output_path = Path(output_path)
    fig, axis = plt.subplots(figsize=(8, 8))

    chip = layout["chip"]
    axis.add_patch(Rectangle((0, 0), chip["width"], chip["height"], fill=False, linewidth=2, edgecolor="black"))

    for obstacle in layout["obstacles"]:
        axis.add_patch(
            Rectangle(
                (obstacle["x"], obstacle["y"]),
                obstacle["width"],
                obstacle["height"],
                facecolor="lightgray",
                edgecolor="dimgray",
            )
        )
        axis.text(obstacle["x"], obstacle["y"] + obstacle["height"] + 10, obstacle["name"], fontsize=8)

    _draw_escape_edges(axis, chip, layout["escape_edges"])
    _draw_starts(axis, layout["control_starts"], "control", "tab:blue", "o")
    _draw_starts(axis, layout["readout_starts"], "readout", "tab:orange", "s")

    for route in routes:
        if not route["success"]:
            continue
        xs = [point[0] for point in route["path"]]
        ys = [point[1] for point in route["path"]]
        color = "tab:blue" if route["route_type"] == "control" else "tab:orange"
        linestyle = "-" if route["route_type"] == "control" else "--"
        axis.plot(xs, ys, linestyle=linestyle, color=color, linewidth=2)
        axis.text(xs[0], ys[0] + 12, route["route_id"], fontsize=8, color=color)

    axis.set_xlim(-40, chip["width"] + 40)
    axis.set_ylim(-40, chip["height"] + 40)
    axis.set_aspect("equal")
    axis.set_title("QEDA-Router Toy Layout Preview")
    axis.set_xlabel("x")
    axis.set_ylabel("y")
    axis.grid(True, linestyle=":", linewidth=0.5)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _draw_escape_edges(axis, chip: dict, escape_edges: dict) -> None:
    if escape_edges.get("left"):
        axis.plot([0, 0], [0, chip["height"]], color="green", linewidth=4, alpha=0.25)
    if escape_edges.get("right"):
        axis.plot([chip["width"], chip["width"]], [0, chip["height"]], color="green", linewidth=4, alpha=0.25)
    if escape_edges.get("bottom"):
        axis.plot([0, chip["width"]], [0, 0], color="green", linewidth=4, alpha=0.25)
    if escape_edges.get("top"):
        axis.plot([0, chip["width"]], [chip["height"], chip["height"]], color="green", linewidth=4, alpha=0.25)


def _draw_starts(axis, items: list[dict], label: str, color: str, marker: str) -> None:
    if not items:
        return
    axis.scatter([item["x"] for item in items], [item["y"] for item in items], color=color, marker=marker, label=label)
    axis.legend(loc="upper right")

