from backend.models.scene import SceneRequirements

from backend.services.music_search import (
    search_candidate_tracks
)


def search_music_catalog_tool(
    mood: list[str],
    energy: int,
    bpm_min: int,
    bpm_max: int,
    genres: list[str],
    instrumentation: list[str],
    pacing: str,
    scene_duration_seconds: int,
    budget: float,
    territory: str
) -> dict:
    """
    Search the SyncAgent music catalog for tracks that may
    creatively fit the scene and can be evaluated against
    the user's budget and territory constraints.

    Use this tool after scene analysis.

    Args:
        mood: Desired moods.
        energy: Desired energy level from 1 to 5.
        bpm_min: Minimum desired BPM.
        bpm_max: Maximum desired BPM.
        genres: Desired music genres.
        instrumentation: Desired instruments.
        pacing: Scene pacing.
        scene_duration_seconds: Estimated scene duration.
        budget: Maximum available music licensing budget.
        territory: Required usage territory.

    Returns:
        Candidate music tracks from the catalog.
    """

    requirements = SceneRequirements(
        mood=mood[:3],
        energy=energy,
        bpm_min=bpm_min,
        bpm_max=bpm_max,
        genres=genres[:3],
        instrumentation=instrumentation,
        pacing=pacing,
        scene_duration_seconds=scene_duration_seconds
    )

    tracks = search_candidate_tracks(
        requirements
    )

    return {
        "candidate_count": len(tracks),

        "tracks": [
            track.model_dump()
            for track in tracks
        ]
    }