from qeda_router.routing_templates import build_simplified_templates


def test_templates_include_straight_turn_and_offset():
    templates = build_simplified_templates(10)
    assert set(templates) == {"straight", "turn", "offset"}
    assert len(templates["straight"]) >= 2
    assert templates["turn"][0][-1] == (10, 10)

