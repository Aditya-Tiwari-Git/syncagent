from backend.models.scene import SceneRequirements
from backend.services.music_search import (
    search_candidate_tracks
)


requirements = SceneRequirements(
    mood=["dark", "melancholic"],
    energy=2,
    bpm_min=60,
    bpm_max=80,
    genres=["cinematic", "ambient"],
    instrumentation=["piano", "strings"],
    pacing="slow"
)


tracks = search_candidate_tracks(
    requirements
)

print(f"\nFound {len(tracks)} tracks\n")

for track in tracks[:10]:

    print(
        f"{track.title} | "
        f"{track.mood} | "
        f"{track.genre} | "
        f"{track.bpm} BPM | "
        f"${track.license_price}"
    )