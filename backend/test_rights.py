from backend.models.track import Track
from backend.services.rights_validator import (
    validate_track
)


track = Track(
    id="TRK001",
    title="Midnight Shadows",
    artist="Demo Artist",
    genre="cinematic",
    mood="melancholic",
    bpm=72,
    energy=2,
    duration_seconds=180,
    instrumentation="piano, strings",
    sync_available=False,
    commercial_use=True,
    territory="worldwide",
    license_price=500,
    license_type="sync_demo"
)


result = validate_track(
    track=track,
    budget=300,
    territory="worldwide"
)


print("Valid:", result.valid)

print("\nReasons:")

for reason in result.rejection_reasons:

    print("-", reason)