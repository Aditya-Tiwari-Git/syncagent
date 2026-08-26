from backend.services.scene_analyzer import (
    analyze_scene
)

from backend.services.music_search import (
    search_candidate_tracks
)

from backend.services.recommendations import (
    rank_tracks, get_match_label
)

from backend.services.normalizer import (
    normalize_moods
)


def print_line():

    print("=" * 70)


def main():

    scene = """
A woman slowly walks through a dark,
abandoned building.

She hears footsteps behind her but
cannot see anyone.

The tension increases as she approaches
a locked door.
"""


    print_line()

    print("SYNCAGENT - MUSIC MATCHING")

    print_line()


    # STEP 1
    print("\nANALYZING SCENE...\n")

    requirements = analyze_scene(
        scene
    )

    requirements.mood = normalize_moods(
        requirements.mood
    )

    print(
        requirements.model_dump_json(
            indent=4
        )
    )


    # STEP 2
    print("\nSEARCHING MUSIC CATALOG...\n")

    candidates = search_candidate_tracks(
        requirements
    )

    print(
        f"Candidates found: "
        f"{len(candidates)}"
    )


    # STEP 3
    print("\nCALCULATING CREATIVE MATCH...\n")

    recommendations = rank_tracks(
        candidates,
        requirements
    )

    if not recommendations:

      print(
          "\nNo strong creative matches found."
      )

      print(
          "\nClosest alternatives:"
      )

      from backend.services.recommendations import (
          find_closest_alternatives
      )

      alternatives = (
          find_closest_alternatives(
              candidates,
              requirements
          )
      )

      for alternative in alternatives:

          print(
              f"\n{alternative.track.title}"
          )

          print(
              f"Match: "
              f"{alternative.final_score}%"
          )


    # STEP 4
    print_line()

    print("TOP 5 MUSIC MATCHES")

    print_line()


    for index, recommendation in enumerate(
        recommendations[:5],
        start=1
    ):

        track = recommendation.track

        print(
            f"\n#{index} "
            f"{track.title}"
        )

        print(
            f"Artist: "
            f"{track.artist}"
        )

        print(
            f"Final Match: "
            f"{recommendation.final_score}%"
        )

        label = get_match_label(
            recommendation.final_score
        )

        print(
            f"Match Quality: {label}"
        )

        print(
            f"Mood: "
            f"{track.mood}"
        )

        print(
            f"Genre: "
            f"{track.genre}"
        )

        print(
            f"BPM: "
            f"{track.bpm}"
        )

        print(
            f"Energy: "
            f"{track.energy}"
        )

        print(
            f"Price: "
            f"${track.license_price}"
        )

        print(
            "\nWhy it matches:"
        )

        print(
            recommendation.match_explanation
        )

        print(
            "\nScore Breakdown:"
        )

        for key, value in (
            recommendation
            .score_breakdown
            .items()
        ):

            print(
                f"  {key}: {value}"
            )


if __name__ == "__main__":

    main()