from qeda_router.single_side_router import build_route_specs, route_layout


def test_single_side_router_connects_start_to_boundary():
    layout = {
        "chip": {"width": 100, "height": 100, "grid_size": 10},
        "process": {"d1": 10, "d2": 20, "db": 0, "r": 20},
        "escape_edges": {"left": True, "right": False, "top": False, "bottom": False},
        "obstacles": [],
        "control_starts": [{"name": "c1", "x": 50, "y": 50}],
        "readout_starts": [],
        "warnings": [],
    }
    order = [route["route_id"] for route in build_route_specs(layout)]
    result = route_layout(layout, order)
    assert result["success_count"] == 1
    assert result["routes"][0]["path"][-1][0] == 0

