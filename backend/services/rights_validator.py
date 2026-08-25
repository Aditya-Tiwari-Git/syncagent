"""Track validation service for rights and licensing.

Validates tracks against licensing and rights requirements.
"""

import logging

from backend.models.track import Track, ValidatedTrack

logger = logging.getLogger(__name__)


def validate_track(
    track: Track,
    budget: float,
    territory: str,
    require_commercial_use: bool = True,
) -> ValidatedTrack:
    """Validate a track against licensing and rights requirements.
    
    Checks:
    1. Sync rights availability
    2. Commercial use permission (if required)
    3. Budget constraints
    4. Territory restrictions
    
    Args:
        track: Track to validate
        budget: Maximum budget in USD
        territory: Required territory (e.g., 'india', 'worldwide')
        require_commercial_use: Whether commercial use is required
        
    Returns:
        ValidatedTrack with validation results and rejection reasons
        
    Example:
        >>> track = Track(...)
        >>> result = validate_track(track, budget=500, territory="worldwide")
        >>> if result.valid:
        ...     print(f"Track approved: {track.title}")
        ... else:
        ...     print(f"Reasons: {result.rejection_reasons}")
    """
    reasons: list[str] = []

    # Rule 1: Sync rights
    if not track.sync_available:
        reasons.append("Sync rights are not available.")
        logger.debug(f"Track {track.id} rejected: no sync rights")

    # Rule 2: Commercial use
    if require_commercial_use and not track.commercial_use:
        reasons.append("Commercial use is not permitted.")
        logger.debug(f"Track {track.id} rejected: no commercial use")

    # Rule 3: Budget
    if track.license_price > budget:
        reasons.append(
            f"License price (${track.license_price:.2f}) "
            f"exceeds the budget (${budget:.2f})."
        )
        logger.debug(
            f"Track {track.id} rejected: price {track.license_price} > budget {budget}"
        )

    # Rule 4: Territory
    track_territory = track.territory.lower()
    requested_territory = territory.lower()

    if (
        track_territory != "worldwide"
        and track_territory != requested_territory
    ):
        reasons.append(
            f"Track is only available for '{track.territory}' territory."
        )
        logger.debug(
            f"Track {track.id} rejected: territory {track.territory} != {territory}"
        )

    valid = len(reasons) == 0
    
    if valid:
        logger.debug(f"Track {track.id} passed validation")
    
    return ValidatedTrack(
        track=track,
        valid=valid,
        rejection_reasons=reasons,
    )