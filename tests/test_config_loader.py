from qeda_router.config_loader import load_layout, validate_layout_dict


def test_validate_layout_dict_accepts_minimal_layout():
    layout = {
        "chip": {"width": 100, "height": 100, "grid_size": 10},
        "process": {"d1": 20, "d2": 40, "db": 10, "r": 30},
        "escape_edges": {"left": True, "right": True, "top": False, "bottom": False},
        "obstacles": [],
        "control_starts": [{"name": "c1", "x": 20, "y": 20}],
        "readout_starts": [],
    }
    normalized, errors, warnings = validate_layout_dict(layout)
    assert not errors
    assert normalized["chip"]["grid_size"] == 10
    assert warnings


def test_load_layout_reads_example_file():
    layout = load_layout("examples/4qubit/layout.yaml")
    assert layout["chip"]["width"] == 1000
    assert len(layout["control_starts"]) == 4

