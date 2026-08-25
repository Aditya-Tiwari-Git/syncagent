from backend.models.scene import SceneRequirements
from backend.models.track import Track

def calculate_mood_score(
    track: Track,
    requirements: SceneRequirements
) -> float:

    track_moods = [
        mood.strip().lower()
        for mood in track.mood.split(",")
    ]

    required_moods = [
        mood.lower()
        for mood in requirements.mood
    ]

    matches = set(track_moods).intersection(
        set(required_moods)
    )

    if not matches:
        return 0.0

    match_ratio = (
        len(matches)
        / len(required_moods)
    )

    return round(
        match_ratio * 100,
        2
    )



def calculate_bpm_score(
    track: Track,
    requirements: SceneRequirements
) -> float:

    if (
        requirements.bpm_min
        <= track.bpm
        <= requirements.bpm_max
    ):

        return 100.0

    if track.bpm < requirements.bpm_min:

        difference = (
            requirements.bpm_min
            - track.bpm
        )

    else:

        difference = (
            track.bpm
            - requirements.bpm_max
        )

    # Gradually reduce score
    score = max(
        0,
        100 - (difference * 5)
    )

    return round(score, 2)

def calculate_genre_score(
    track: Track,
    requirements: SceneRequirements
) -> float:

    track_genres = [
        genre.strip().lower()
        for genre in track.genre.split(",")
    ]

    required_genres = [
        genre.lower()
        for genre in requirements.genres
    ]

    matches = set(track_genres).intersection(
        set(required_genres)
    )

    if not matches:
        return 0.0

    return round(
        (
            len(matches)
            / len(required_genres)
        ) * 100,
        2
    )

def calculate_energy_score(
    track: Track,
    requirements: SceneRequirements
) -> float:

    difference = abs(
        track.energy
        - requirements.energy
    )

    if difference == 0:
        return 100.0

    if difference == 1:
        return 75.0

    if difference == 2:
        return 40.0

    if difference == 3:
        return 15.0

    return 0.0

def calculate_instrumentation_score(
    track: Track,
    requirements: SceneRequirements
) -> float:

    track_instruments = [
        instrument.strip().lower()
        for instrument
        in track.instrumentation.split(",")
    ]

    required_instruments = [
        instrument.lower()
        for instrument
        in requirements.instrumentation
    ]

    matches = set(
        track_instruments
    ).intersection(
        set(required_instruments)
    )

    if not matches:
        return 0.0

    return round(
        (
            len(matches)
            / len(required_instruments)
        ) * 100,
        2
    )

def calculate_duration_score(
    track: Track,
    requirements: SceneRequirements
) -> float:

    scene_duration = (
        requirements.scene_duration_seconds
    )

    track_duration = (
        track.duration_seconds
    )

    if track_duration >= scene_duration:

        return 100.0

    difference = (
        scene_duration
        - track_duration
    )

    score = max(
        0,
        100 - difference
    )

    return round(score, 2)

def calculate_match_score(
    track: Track,
    requirements: SceneRequirements
) -> dict:

    mood_score = calculate_mood_score(
        track,
        requirements
    )

    bpm_score = calculate_bpm_score(
        track,
        requirements
    )

    genre_score = calculate_genre_score(
        track,
        requirements
    )

    energy_score = calculate_energy_score(
        track,
        requirements
    )

    instrumentation_score = (
        calculate_instrumentation_score(
            track,
            requirements
        )
    )

    duration_score = (
        calculate_duration_score(
            track,
            requirements
        )
    )

    final_score = (
        mood_score * 0.40
        + bpm_score * 0.20
        + genre_score * 0.15
        + energy_score * 0.15
        + instrumentation_score * 0.05
        + duration_score * 0.05
    )

    return {
        "final_score": round(
            final_score,
            2
        ),

        "mood_score": mood_score,

        "bpm_score": bpm_score,

        "genre_score": genre_score,

        "energy_score": energy_score,

        "instrumentation_score":
            instrumentation_score,

        "duration_score":
            duration_score,
    }