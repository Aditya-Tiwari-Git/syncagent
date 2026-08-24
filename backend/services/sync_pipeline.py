from backend.services.scene_analyzer import (
    analyze_scene
)

from backend.services.music_search import (
    search_candidate_tracks
)

from backend.services.rights_validator import (
    validate_track
)

from backend.services.ranking import (
    calculate_creative_score,
    calculate_final_score,
)


def run_syncagent_pipeline(
    scene: str,
    budget: float,
    territory: str,
):

    requirements = analyze_scene(scene)

    candidates = search_candidate_tracks(
        requirements
    )

    valid_tracks = []

    rejected_tracks = []


    for track in candidates:

        validation = validate_track(
            track=track,
            budget=budget,
            territory=territory,
        )

        if validation.valid:

            creative_score = (
                calculate_creative_score(
                    track=track,
                    requirements=requirements,
                )
            )

            final_score = (
                calculate_final_score(
                    creative_score=creative_score,
                    track=track,
                    budget=budget,
                )
            )

            validation.creative_score = (
                creative_score
            )

            validation.final_score = (
                final_score
            )

            valid_tracks.append(
                validation
            )

        else:

            rejected_tracks.append(
                validation
            )


    ranked_tracks = sorted(
        valid_tracks,
        key=lambda x: x.final_score,
        reverse=True,
    )


    return {
        "requirements": requirements,
        "recommendations": ranked_tracks,
        "rejected": rejected_tracks,
    }