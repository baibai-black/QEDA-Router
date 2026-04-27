from qeda_router.sequence_search import run_sequence_search


def test_sequence_search_returns_best_result():
    layout = {
        "chip": {"width": 100, "height": 100, "grid_size": 10},
        "process": {"d1": 10, "d2": 20, "db": 0, "r": 20},
        "escape_edges": {"left": True, "right": True, "top": False, "bottom": False},
        "obstacles": [{"name": "obs", "type": "rectangle", "x": 40, "y": 0, "width": 20, "height": 60}],
        "control_starts": [{"name": "c1", "x": 30, "y": 80}, {"name": "c2", "x": 70, "y": 80}],
        "readout_starts": [],
        "warnings": [],
    }
    result = run_sequence_search(layout)
    assert result["best_result"]["sequence_name"] in {"input_order", "reversed_order", "boundary_distance_order"}
    assert len(result["candidates"]) == 3

