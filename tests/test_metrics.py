from qeda_router.metrics import corner_count, path_length


def test_metrics_compute_length_and_corners():
    path = [(0, 0), (10, 0), (10, 20), (30, 20)]
    assert path_length(path) == 50
    assert corner_count(path) == 2
