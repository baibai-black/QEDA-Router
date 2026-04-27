from qeda_router.drc import run_basic_drc


def test_drc_detects_spacing_and_obstacle_collision():
    layout = {
        "chip": {"width": 100, "height": 100, "grid_size": 10},
        "process": {"d1": 20, "d2": 30, "db": 10, "r": 20},
        "escape_edges": {"left": True, "right": True, "top": True, "bottom": True},
        "obstacles": [{"name": "obs", "type": "rectangle", "x": 40, "y": 40, "width": 10, "height": 10}],
        "control_starts": [],
        "readout_starts": [],
    }
    routes = [
        {
            "route_id": "c1",
            "route_type": "control",
            "success": True,
            "path": [(0, 0), (40, 40), (60, 40)],
            "corner_count": 1,
        },
        {
            "route_id": "r1",
            "route_type": "readout",
            "success": True,
            "path": [(0, 10), (40, 40), (60, 50)],
            "corner_count": 1,
        },
    ]
    report = run_basic_drc(layout, routes)
    messages = [item["message"] for item in report["warnings"]]
    assert any("obstacle keep-out" in message for message in messages)
    assert any("Spacing" in message for message in messages)

