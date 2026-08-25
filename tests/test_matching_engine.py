from backend.models.scene import (
    SceneRequirements
)

from backend.models.track import (
    Track
)

from backend.services.matching import (
    calculate_match_score
)


requirements = SceneRequirements(

    mood=[
        "dark",
        "melancholic"
    ],

    energy=2,

    bpm_min=60,
    bpm_max=80,

    genres=[
        "cinematic",
        "ambient"
    ],

    instrumentation=[
        "piano",
        "strings"
    ],

    pacing="slow",

    scene_duration_seconds=90
)


track = Track(

    id="TRK002",

    title="Happy Morning",

    artist="Demo Artist",

    genre="acoustic",

    mood="happy",

    bpm=140,

    energy=5,

    duration_seconds=60,

    instrumentation="guitar, drums",

    sync_available=True,

    commercial_use=True,

    territory="worldwide",

    license_price=200,

    license_type="sync_demo"
)


def test_calculate_match_score_returns_expected_components():
    """Ensure the matcher returns bounded component scores."""
    result = calculate_match_score(track, requirements)

    assert set(result) == {
        "final_score",
        "mood_score",
        "bpm_score",
        "genre_score",
        "energy_score",
        "instrumentation_score",
        "duration_score",
    }
    assert result["final_score"] == 5.75
    assert all(0 <= score <= 100 for score in result.values())