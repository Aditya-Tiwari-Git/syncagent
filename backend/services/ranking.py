from backend.models.scene import SceneRequirements
from backend.models.track import Track


def calculate_creative_score(
    track: Track,
    requirements: SceneRequirements
) -> float:

    score = 0.0

    # -------------------------
    # MOOD
    # Weight: 40 points
    # -------------------------

    track_mood = track.mood.lower()

    if track_mood in requirements.mood:

        score += 40


    # -------------------------
    # BPM
    # Weight: 20 points
    # -------------------------

    if (
        requirements.bpm_min
        <= track.bpm
        <= requirements.bpm_max
    ):

        score += 20


    # -------------------------
    # GENRE
    # Weight: 15 points
    # -------------------------

    if track.genre.lower() in requirements.genres:

        score += 15


    # -------------------------
    # ENERGY
    # Weight: 15 points
    # -------------------------

    energy_difference = abs(
        track.energy
        - requirements.energy
    )

    if energy_difference == 0:

        score += 15

    elif energy_difference == 1:

        score += 10

    elif energy_difference == 2:

        score += 5


    # -------------------------
    # INSTRUMENTATION
    # Weight: 10 points
    # -------------------------

    track_instruments = [
        item.strip().lower()
        for item in track.instrumentation.split(",")
    ]

    matching_instruments = set(
        track_instruments
    ).intersection(
        set(requirements.instrumentation)
    )

    if matching_instruments:

        score += 10


    return round(score, 2)

def calculate_final_score(
    creative_score: float,
    track: Track,
    budget: float
) -> float:

    score = creative_score

    # Bonus for being significantly under budget
    if track.license_price <= budget * 0.5:

        score += 5

    elif track.license_price <= budget * 0.75:

        score += 2

    return round(
        min(score, 100),
        2
    )