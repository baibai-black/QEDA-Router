from qeda_router.grid_model import GridModel


def test_grid_model_marks_obstacle_cells():
    grid = GridModel(chip_width=100, chip_height=100, grid_size=10)
    grid.mark_obstacles(
        [{"name": "obs", "type": "rectangle", "x": 40, "y": 40, "width": 20, "height": 20}],
        clearance=0,
    )
    assert (4, 4) in grid.obstacle_blocked
    assert (0, 0) not in grid.obstacle_blocked

