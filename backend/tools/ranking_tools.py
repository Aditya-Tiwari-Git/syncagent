from backend.models.scene import (
    SceneRequirements
)

from backend.models.track import (
    Track
)

from backend.services.recommendations import (
    rank_tracks
)


def rank_music_candidates_tool(
    tracks_data: list[dict],
    mood: list[str],
    energy: int,
    bpm_min: int,
    bpm_max: int,
    genres: list[str],
    instrumentation: list[str],
    pacing: str,
    scene_duration_seconds: int,
    limit: int = 5
) -> dict:
    """
    Rank music candidates according to creative compatibility
    with the analyzed film scene.

    Use this only after candidates have passed the configured
    licensing and pre-clearance checks.

    Args:
        tracks_data: Candidate tracks that passed validation.
        mood: Desired scene moods.
        energy: Desired scene energy.
        bpm_min: Minimum BPM.
        bpm_max: Maximum BPM.
        genres: Desired genres.
        instrumentation: Desired instruments.
        pacing: Scene pacing.
        scene_duration_seconds: Estimated scene duration.
        limit: Maximum number of recommendations.

    Returns:
        Ranked recommendations with creative match scores
        and explanations.
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

    tracks = [
        Track(**track)
        for track in tracks_data
    ]

    recommendations = rank_tracks(
        tracks,
        requirements
    )

    return {
        "recommendations": [
            recommendation.model_dump()
            for recommendation
            in recommendations[:limit]
        ]
    }