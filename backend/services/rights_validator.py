from backend.models.track import (
    Track,
    ValidatedTrack
)


def validate_track(
    track: Track,
    budget: float,
    territory: str,
    require_commercial_use: bool = True,
) -> ValidatedTrack:

    reasons = []

    # Rule 1: Sync rights
    if not track.sync_available:

        reasons.append(
            "Sync rights are not available."
        )

    # Rule 2: Commercial use
    if (
        require_commercial_use
        and not track.commercial_use
    ):

        reasons.append(
            "Commercial use is not permitted."
        )

    # Rule 3: Budget
    if track.license_price > budget:

        reasons.append(
            f"License price (${track.license_price}) "
            f"exceeds the budget (${budget})."
        )

    # Rule 4: Territory
    track_territory = track.territory.lower()
    requested_territory = territory.lower()

    if (
        track_territory != "worldwide"
        and track_territory != requested_territory
    ):

        reasons.append(
            f"Track is only available for "
            f"'{track.territory}' territory."
        )

    valid = len(reasons) == 0

    return ValidatedTrack(
        track=track,
        valid=valid,
        rejection_reasons=reasons,
    )