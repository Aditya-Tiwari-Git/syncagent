from backend.models.track import Track
from backend.services.rights_validator import validate_track


def validate_music_rights_tool(
    track: Track,
    budget: float,
    territory: str,
) -> dict:
    """
    Validate a music catalog track against deterministic
    pre-clearance rules.

    Checks:
    - sync availability
    - commercial usage
    - budget
    - territory

    This is not legal clearance.
    """

    result = validate_track(
        track=track,
        budget=budget,
        territory=territory,
    )

    return result.model_dump()
