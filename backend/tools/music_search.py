import os
from pathlib import Path

import clickhouse_connect
from dotenv import load_dotenv


# ============================================================
# Database connection
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV_FILE = BASE_DIR / ".env.example"

load_dotenv(ENV_FILE)


def get_clickhouse_client():
    """
    Create and return a ClickHouse client.
    """

    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST"),
        user=os.getenv("CLICKHOUSE_USER"),
        password=os.getenv("CLICKHOUSE_PASSWORD"),
        secure=True,
    )


# ============================================================
# Music search
# ============================================================

def search_tracks(
    mood=None,
    bpm_min=None,
    bpm_max=None,
    genre=None,
    budget=None,
    territory=None,
):
    """
    Search the music catalog based on the supplied parameters.

    Parameters
    ----------
    mood : str, optional
        Desired mood, e.g. "melancholic", "happy".

    bpm_min : int, optional
        Minimum BPM.

    bpm_max : int, optional
        Maximum BPM.

    genre : str, optional
        Desired genre, e.g. "cinematic", "ambient".

    budget : float, optional
        Maximum acceptable license price.

    territory : str, optional
        Required territory, e.g. "india", "us", "worldwide".

    Returns
    -------
    list[dict]
        Matching tracks.
    """

    client = get_clickhouse_client()

    conditions = [
        "sync_available = true",
        "commercial_use = true",
    ]

    parameters = {}

    # --------------------------------------------------------
    # Mood
    # --------------------------------------------------------

    if mood:
        conditions.append("mood = {mood:String}")
        parameters["mood"] = mood

    # --------------------------------------------------------
    # BPM
    # --------------------------------------------------------

    if bpm_min is not None:
        conditions.append("bpm >= {bpm_min:UInt16}")
        parameters["bpm_min"] = bpm_min

    if bpm_max is not None:
        conditions.append("bpm <= {bpm_max:UInt16}")
        parameters["bpm_max"] = bpm_max

    # --------------------------------------------------------
    # Genre
    # --------------------------------------------------------

    if genre:
        conditions.append("genre = {genre:String}")
        parameters["genre"] = genre

    # --------------------------------------------------------
    # Budget
    # --------------------------------------------------------

    if budget is not None:
        conditions.append("license_price <= {budget:Float64}")
        parameters["budget"] = budget

    # --------------------------------------------------------
    # Territory
    # --------------------------------------------------------

    if territory:
        conditions.append(
            """
            (
                territory = {territory:String}
                OR territory = 'worldwide'
            )
            """
        )
        parameters["territory"] = territory

    # --------------------------------------------------------
    # Build query
    # --------------------------------------------------------

    where_clause = " AND ".join(conditions)

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
        WHERE {where_clause}
        ORDER BY license_price ASC
        LIMIT 50
    """

    # --------------------------------------------------------
    # Execute query
    # --------------------------------------------------------

    result = client.query(
        query,
        parameters=parameters,
    )

    # --------------------------------------------------------
    # Convert ClickHouse rows to dictionaries
    # --------------------------------------------------------

    columns = result.column_names

    tracks = [
        dict(zip(columns, row))
        for row in result.result_rows
    ]

    return tracks


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    results = search_tracks(
        mood="melancholic",
        bpm_min=60,
        bpm_max=100,
        genre="cinematic",
        budget=1000,
        territory="india",
    )

    print(f"Found {len(results)} tracks")

    for track in results:
        print(
            f"{track['id']} | "
            f"{track['title']} | "
            f"{track['artist']} | "
            f"{track['mood']} | "
            f"{track['genre']} | "
            f"{track['bpm']} BPM | "
            f"₹{track['license_price']}"
        )
