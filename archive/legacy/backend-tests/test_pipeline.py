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
    calculate_final_score
)

from backend.services.recommendations import generate_no_match_suggestions


def print_line():

    print("=" * 60)


def main():

    scene = """
    A detective walks alone through an empty Mumbai
    street at 2 AM after failing to solve a murder case.

    It is raining lightly.

    He feels exhausted, isolated and hopeless.
    """

    budget = 1000

    territory = "worldwide"


    print_line()

    print("SYNCAGENT")

    print_line()

    print("\nSCENE:\n")

    print(scene)


    # ---------------------------------
    # STEP 1
    # GEMINI ANALYSIS
    # ---------------------------------

    print("\nANALYZING SCENE WITH GEMINI...\n")

    requirements = analyze_scene(
        scene
    )

    print(
        requirements.model_dump_json(
            indent=4
        )
    )


    # ---------------------------------
    # STEP 2
    # CLICKHOUSE SEARCH
    # ---------------------------------

    print("\nSEARCHING CLICKHOUSE...\n")

    candidates = search_candidate_tracks(
        requirements
    )

    print(
        f"Found {len(candidates)} "
        f"candidate tracks."
    )


    # ---------------------------------
    # STEP 3
    # RIGHTS VALIDATION
    # ---------------------------------

    print("\nVALIDATING RIGHTS...\n")

    valid_tracks = []

    rejected_tracks = []

    for track in candidates:

        validation = validate_track(
            track=track,
            budget=budget,
            territory=territory,
            require_commercial_use=True,
        )

        if validation.valid:

            valid_tracks.append(
                validation
            )

        else:

            rejected_tracks.append(
                validation
            )


    print(
        f"Valid tracks: "
        f"{len(valid_tracks)}"
    )

    print(
        f"Rejected tracks: "
        f"{len(rejected_tracks)}"
    )


    # ---------------------------------
    # STEP 4
    # RANKING
    # ---------------------------------

    print("\nRANKING TRACKS...\n")

    for item in valid_tracks:

        creative_score = (
            calculate_creative_score(
                track=item.track,
                requirements=requirements,
            )
        )

        final_score = (
            calculate_final_score(
                creative_score=creative_score,
                track=item.track,
                budget=budget,
            )
        )

        item.creative_score = creative_score

        item.final_score = final_score


    ranked_tracks = sorted(
        valid_tracks,
        key=lambda item: item.final_score,
        reverse=True,
    )


    # ---------------------------------
    # RESULTS
    # ---------------------------------

    print_line()

    print("TOP RECOMMENDATIONS")

    print_line()


    if not ranked_tracks:

        print(
            "\nNo tracks satisfy all "
            "configured constraints."
        )
        suggestions = (
            generate_no_match_suggestions(
                budget=budget,
                rejected_tracks=rejected_tracks,
            )
        )

        print("\nSuggested next actions:\n")

        for suggestion in suggestions:

            print(f"• {suggestion}")


    else:

        for index, item in enumerate(
            ranked_tracks[:5],
            start=1
        ):

            track = item.track

            print(
                f"\n{index}. {track.title}"
            )

            print(
                f"   Artist: {track.artist}"
            )

            print(
                f"   Mood: {track.mood}"
            )

            print(
                f"   Genre: {track.genre}"
            )

            print(
                f"   BPM: {track.bpm}"
            )

            print(
                f"   Price: "
                f"${track.license_price}"
            )

            print(
                f"   Creative Score: "
                f"{item.creative_score}"
            )

            print(
                f"   Final Score: "
                f"{item.final_score}"
            )


    # ---------------------------------
    # REJECTED TRACKS
    # ---------------------------------

    print("\n")

    print_line()

    print("REJECTED CANDIDATES")

    print_line()


    for item in rejected_tracks[:10]:

        print(
            f"\n{item.track.title}"
        )

        for reason in item.rejection_reasons:

            print(
                f"   ❌ {reason}"
            )


if __name__ == "__main__":

    main()