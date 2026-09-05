from backend.models.track import Track
from backend.tools.rights_tools import validate_music_rights_tool


track = Track(
    id="TR001",
    title="Rain at 2AM",
    artist="Test Artist",
    genre="Ambient",
    mood="melancholic",
    bpm=60,
    energy=2,
    duration_seconds=180,
    instrumentation="piano, cello, atmospheric synths",
    sync_available=True,
    commercial_use=True,
    territory="worldwide",
    license_price=500,
    license_type="standard_sync",
)


result = validate_music_rights_tool(
    track=track,
    budget=800,
    territory="worldwide",
)

print(result)
