"""Music search service using ClickHouse database.

Searches for music tracks matching scene requirements.
"""

import logging
from typing import Optional

import clickhouse_connect

from backend.config import settings
from backend.models.scene import SceneRequirements
from backend.models.track import Track

logger = logging.getLogger(__name__)


def get_clickhouse_client() -> clickhouse_connect.driver.Client:
    """Create and return a ClickHouse client.
    
    Returns:
        ClickHouse client connection
        
    Raises:
        Exception: If connection fails (missing credentials, network error)
    """
    try:
        client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            username=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
            secure=True,
        )
        logger.debug("ClickHouse client created successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create ClickHouse client: {e}")
        raise


def search_candidate_tracks(
    requirements: SceneRequirements,
    limit: int = 100
) -> list[Track]:
    """Search for music tracks matching scene requirements.
    
    Queries the ClickHouse database for tracks within the required BPM range.
    This is the primary filtering step; additional scoring happens later.
    
    Args:
        requirements: Scene musical requirements
        limit: Maximum number of results to return (default 100)
        
    Returns:
        List of Track objects matching the BPM criteria
        
    Raises:
        Exception: If database query fails
        
    Example:
        >>> from backend.models.scene import SceneRequirements
        >>> reqs = SceneRequirements(
        ...     mood=["dark"],
        ...     energy=2,
        ...     bpm_min=60,
        ...     bpm_max=80,
        ...     genres=["ambient"],
        ...     instrumentation=["piano"],
        ...     pacing="slow"
        ... )
        >>> tracks = search_candidate_tracks(reqs)
        >>> len(tracks)
        42
    """
    logger.info(
        f"Searching for tracks: BPM {requirements.bpm_min}-{requirements.bpm_max}, "
        f"Energy {requirements.energy}, Genres {requirements.genres}"
    )

    try:
        client = get_clickhouse_client()
    except Exception as e:
        logger.error(f"Failed to get ClickHouse client: {e}")
        raise

    query = f"""
    SELECT
        id,
        title,
        artist,
        genre,
        mood,
        bpm,
        energy,
        duration_seconds,
        instrumentation,
        sync_available,
        commercial_use,
        territory,
        license_price,
        license_type
    FROM tracks
    WHERE bpm BETWEEN {{bpm_min:UInt16}}
                  AND {{bpm_max:UInt16}}
    LIMIT {limit}
    """

    try:
        result = client.query(
            query,
            parameters={
                "bpm_min": requirements.bpm_min,
                "bpm_max": requirements.bpm_max,
            }
        )
        logger.debug(f"Query returned {len(result.result_rows)} rows")
    except Exception as e:
        logger.error(f"ClickHouse query failed: {e}")
        raise

    tracks = []
    for row in result.named_results():
        try:
            track = Track(
                id=row["id"],
                title=row["title"],
                artist=row["artist"],
                genre=row["genre"],
                mood=row["mood"],
                bpm=row["bpm"],
                energy=row["energy"],
                duration_seconds=row["duration_seconds"],
                instrumentation=row["instrumentation"],
                sync_available=row["sync_available"],
                commercial_use=row["commercial_use"],
                territory=row["territory"],
                license_price=row["license_price"],
                license_type=row["license_type"],
            )
            tracks.append(track)
        except Exception as e:
            logger.warning(f"Failed to parse track row: {e}")
            continue

    logger.info(f"Found {len(tracks)} candidate tracks")
    return tracks