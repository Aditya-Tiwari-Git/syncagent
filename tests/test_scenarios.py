from scenarios import SCENARIOS
from database.seed_catalog import DEMO_TRACKS, build_catalog


def test_scenario_catalog_is_complete_and_unique():
    assert len(SCENARIOS) >= 20
    names = [scenario["name"] for scenario in SCENARIOS]
    assert len(names) == len(set(names))
    for scenario in SCENARIOS:
        assert scenario["scene_description"]
        assert scenario["budget"] >= 0
        assert scenario["territory"]
        assert 1 <= scenario["top_k"] <= 10
        assert scenario["expected_behavior"]
        assert scenario["what_to_verify"]


def test_seed_catalog_has_reproducible_demo_and_generated_tracks():
    first = build_catalog(500, 42)
    second = build_catalog(500, 42)

    assert len(DEMO_TRACKS) == 15
    assert len(first) == 500
    assert first == second
    assert first[0]["id"] == "TRK-DEMO-001"
    assert first[-1]["id"] == "TRK-GEN-042-0485"
