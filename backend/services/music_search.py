import clickhouse_connect

from backend.config import settings
from backend.models.scene import SceneRequirements
from backend.models.track import Track


def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=settings.CLICKHOUSE_HOST,
        username=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD,
        secure=True,
    )


def search_candidate_tracks(
    requirements: SceneRequirements
) -> list[Track]:

    client = get_clickhouse_client()

    query = """
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
    WHERE bpm BETWEEN {bpm_min:UInt16}
                  AND {bpm_max:UInt16}
    """

    result = client.query(
        query,
        parameters={
            "bpm_min": requirements.bpm_min,
            "bpm_max": requirements.bpm_max,
        }
    )

    tracks = []

    for row in result.named_results():

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

    return tracks