from backend.models.track import (
    Track,
    TrackRecommendation
)

from backend.models.scene import (
    SceneRequirements
)

from backend.services.matching import (
    calculate_match_score
)

MINIMUM_MATCH_SCORE = 50

def generate_no_match_suggestions(
    budget: float,
    rejected_tracks
) -> list[str]:

    suggestions = []

    budget_rejections = 0

    territory_rejections = 0

    rights_rejections = 0


    for item in rejected_tracks:

        reasons = item.rejection_reasons

        for reason in reasons:

            if "exceeds the budget" in reason:

                budget_rejections += 1

            elif "territory" in reason.lower():

                territory_rejections += 1

            elif (
                "sync rights" in reason.lower()
                or "commercial" in reason.lower()
            ):

                rights_rejections += 1


    if budget_rejections > 0:

        suggestions.append(
            "Consider increasing the budget."
        )


    if territory_rejections > 0:

        suggestions.append(
            "Consider relaxing the territory "
            "requirement if appropriate."
        )


    if rights_rejections > 0:

        suggestions.append(
            "Search for alternative tracks "
            "with compatible rights."
        )


    if not suggestions:

        suggestions.append(
            "Consider broadening the creative "
            "requirements."
        )


    return suggestions



def generate_match_explanation(
    track: Track,
    requirements: SceneRequirements,
    scores: dict
) -> str:

    reasons = []

    if scores["mood_score"] >= 50:

        reasons.append(
            "matches the emotional tone"
        )

    if scores["bpm_score"] >= 75:

        reasons.append(
            "fits the requested tempo"
        )

    if scores["genre_score"] >= 50:

        reasons.append(
            "fits the desired genre"
        )

    if scores["energy_score"] >= 75:

        reasons.append(
            "matches the scene energy"
        )

    if scores["instrumentation_score"] >= 50:

        reasons.append(
            "contains suitable instrumentation"
        )

    if not reasons:

        return (
            "This is a partial creative match "
            "with some differences from the "
            "requested musical profile."
        )

    return (
        "This track "
        + ", ".join(reasons)
        + "."
    )


def create_recommendation(
    track: Track,
    requirements: SceneRequirements
) -> TrackRecommendation:

    
    scores = calculate_match_score(
        track,
        requirements
    )

    explanation = (
        generate_match_explanation(
            track,
            requirements,
            scores
        )
    )

    return TrackRecommendation(
        track=track,

        final_score=scores["final_score"],

        score_breakdown={
            "mood": scores["mood_score"],
            "bpm": scores["bpm_score"],
            "genre": scores["genre_score"],
            "energy": scores["energy_score"],
            "instrumentation":
                scores["instrumentation_score"],
            "duration":
                scores["duration_score"],
        },

        match_explanation=explanation,
    )

def rank_tracks(
    tracks: list[Track],
    requirements: SceneRequirements
) -> list[TrackRecommendation]:

    recommendations = []

    for track in tracks:

        recommendation = (
            create_recommendation(
                track,
                requirements
            )
        )

        if (
            recommendation.final_score
            >= MINIMUM_MATCH_SCORE
        ):

            recommendations.append(
                recommendation
            )

    recommendations.sort(
        key=lambda item: item.final_score,
        reverse=True
    )

    return recommendations

def find_closest_alternatives(
    tracks: list[Track],
    requirements: SceneRequirements,
    limit: int = 3
) -> list[TrackRecommendation]:

    all_recommendations = []

    for track in tracks:

        recommendation = (
            create_recommendation(
                track,
                requirements
            )
        )

        all_recommendations.append(
            recommendation
        )

    all_recommendations.sort(
        key=lambda item: item.final_score,
        reverse=True
    )

    return all_recommendations[:limit]

def get_match_label(
    score: float
) -> str:

    if score >= 90:
        return "Excellent Match"

    if score >= 75:
        return "Strong Match"

    if score >= 60:
        return "Good Match"

    if score >= 45:
        return "Partial Match"

    return "Weak Match"