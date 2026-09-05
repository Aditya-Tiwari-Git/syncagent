import os
import random
from pathlib import Path

import clickhouse_connect
from dotenv import load_dotenv


# ============================================================
# Load environment variables
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# Configuration
# ============================================================

NUM_TRACKS = 150

MOODS = [
    "melancholic",
    "dark",
    "hopeful",
    "romantic",
    "suspenseful",
    "happy",
    "tense",
    "peaceful",
    "energetic",
]

GENRES = [
    "cinematic",
    "ambient",
    "orchestral",
    "electronic",
    "acoustic",
    "jazz",
    "dramatic",
]

INSTRUMENTATIONS = [
    "piano",
    "strings",
    "synth",
    "acoustic guitar",
    "electric guitar",
    "violin",
    "cello",
    "orchestra",
    "piano and strings",
    "synth and drums",
    "guitar and piano",
    "brass and percussion",
]

LICENSE_PRICES = [
    100,
    200,
    300,
    500,
    750,
    1000,
    1500,
    2000,
]

LICENSE_TYPES = [
    "standard_sync",
    "premium_sync",
    "indie_sync",
    "festival_sync",
]

TERRITORIES = [
    "india",
    "us",
    "europe",
]

ARTISTS = [
    "Alex Morgan",
    "Luna Fields",
    "The Midnight Ensemble",
    "Evan Brooks",
    "Nova Sound",
    "Aria Collective",
    "Daniel Stone",
    "Echo Theory",
    "Maya Rivers",
    "Silver Frame",
    "Northbound",
    "Velvet Signal",
]

TITLE_PREFIXES = [
    "After",
    "Before",
    "Beyond",
    "Into",
    "Through",
    "Fading",
    "Lost",
    "Silent",
    "Broken",
    "Last",
    "Hidden",
    "Falling",
    "Rising",
    "Chasing",
    "Echoes of",
]

TITLE_WORDS = [
    "Midnight",
    "Rain",
    "Memories",
    "Tomorrow",
    "Dreams",
    "Shadows",
    "Home",
    "Light",
    "Hope",
    "Distance",
    "Silence",
    "Fire",
    "Winter",
    "Summer",
    "Time",
    "Goodbye",
    "Love",
    "Fear",
    "The City",
    "The Unknown",
]


# ============================================================
# Helper functions
# ============================================================

def generate_bpm():
    """
    Generate BPM from one of three cinematic tempo ranges.

    Slow:   55–80
    Medium: 81–120
    Fast:   121–160
    """

    category = random.choice(["slow", "medium", "fast"])

    if category == "slow":
        return random.randint(55, 80)

    if category == "medium":
        return random.randint(81, 120)

    return random.randint(121, 160)


def generate_energy():
    """
    Energy level from 1 to 5.
    """

    return random.randint(1, 5)


def generate_duration():
    """
    Generate a realistic music duration.

    60–300 seconds = 1–5 minutes.
    """

    return random.randint(60, 300)


def generate_title():
    """
    Generate a simple synthetic track title.
    """

    prefix = random.choice(TITLE_PREFIXES)
    word = random.choice(TITLE_WORDS)

    return f"{prefix} {word}"


def generate_track_id(index):
    return f"TRK-{index:04d}"


def generate_normal_track(index):
    """
    Generate a normal/licensable track.
    """

    return {
        "id": generate_track_id(index),
        "title": generate_title(),
        "artist": random.choice(ARTISTS),

        "genre": random.choice(GENRES),
        "mood": random.choice(MOODS),

        "bpm": generate_bpm(),
        "energy": generate_energy(),
        "duration_seconds": generate_duration(),

        "instrumentation": random.choice(INSTRUMENTATIONS),

        "sync_available": True,
        "commercial_use": True,

        "territory": random.choice(TERRITORIES),

        "license_price": random.choice(
            [100, 200, 300, 500, 750, 1000]
        ),

        "license_type": random.choice(LICENSE_TYPES),
    }


def generate_problematic_track(index):
    """
    Deliberately generate a track that SyncAgent
    should reject for one or more reasons.
    """

    track = generate_normal_track(index)

    problem = random.choice([
        "sync_unavailable",
        "commercial_disabled",
        "wrong_territory",
        "too_expensive",
        "multiple_problems",
    ])

    if problem == "sync_unavailable":
        track["sync_available"] = False

    elif problem == "commercial_disabled":
        track["commercial_use"] = False

    elif problem == "wrong_territory":
        track["territory"] = random.choice(TERRITORIES)

    elif problem == "too_expensive":
        track["license_price"] = 2000

    elif problem == "multiple_problems":
        track["sync_available"] = False
        track["commercial_use"] = False
        track["license_price"] = 2000

    return track


# ============================================================
# Generate catalog
# ============================================================

def generate_catalog(num_tracks=NUM_TRACKS):
    """
    Generate a catalog containing normal and problematic tracks.
    """

    tracks = []

    # Roughly 80% valid tracks
    normal_count = int(num_tracks * 0.80)

    # Roughly 20% problematic tracks
    problematic_count = num_tracks - normal_count

    print(f"Generating {normal_count} normal tracks...")
    print(f"Generating {problematic_count} problematic tracks...")

    for index in range(1, normal_count + 1):
        tracks.append(generate_normal_track(index))

    for index in range(
        normal_count + 1,
        num_tracks + 1
    ):
        tracks.append(generate_problematic_track(index))

    # Shuffle so problematic records aren't all at the end.
    random.shuffle(tracks)

    return tracks


# ============================================================
# Connect to ClickHouse
# ============================================================

def get_clickhouse_client():
    """
    Create a ClickHouse Cloud connection.
    """
    # ============================================================
    # Load environment variables
    # ============================================================

    BASE_DIR = Path(__file__).resolve().parent.parent
    ENV_FILE = BASE_DIR / ".env"

    load_dotenv(ENV_FILE)

    required_variables = [
        "CLICKHOUSE_HOST",
        "CLICKHOUSE_USER",
        "CLICKHOUSE_PASSWORD",
    ]

    for variable in required_variables:
        if not os.getenv(variable):
            raise ValueError(
                f"Missing environment variable: {variable}"
            )

    return clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_HOST"],
        user=os.environ["CLICKHOUSE_USER"],
        password=os.environ["CLICKHOUSE_PASSWORD"],
        secure=True,
    )


# ============================================================
# Create table
# ============================================================

def create_table(client):
    """
    Create the tracks table if it doesn't already exist.
    """

    query = """
    CREATE TABLE IF NOT EXISTS tracks
    (
        id String,
        title String,
        artist String,

        genre String,
        mood String,

        bpm UInt16,
        energy UInt8,
        duration_seconds UInt16,

        instrumentation String,

        sync_available Bool,
        commercial_use Bool,

        territory String,

        license_price Float64,
        license_type String
    )
    ENGINE = MergeTree
    ORDER BY id
    """

    client.command(query)

    print("✅ tracks table is ready")


# ============================================================
# Insert tracks
# ============================================================

def insert_tracks(client, tracks):
    """
    Insert generated tracks into ClickHouse.
    """

    rows = []

    for track in tracks:
        rows.append([
            track["id"],
            track["title"],
            track["artist"],

            track["genre"],
            track["mood"],

            track["bpm"],
            track["energy"],
            track["duration_seconds"],

            track["instrumentation"],

            track["sync_available"],
            track["commercial_use"],

            track["territory"],

            track["license_price"],
            track["license_type"],
        ])

    client.insert(
        "tracks",
        rows,
        column_names=[
            "id",
            "title",
            "artist",
            "genre",
            "mood",
            "bpm",
            "energy",
            "duration_seconds",
            "instrumentation",
            "sync_available",
            "commercial_use",
            "territory",
            "license_price",
            "license_type",
        ],
    )

    print(f"✅ Inserted {len(rows)} tracks")


# ============================================================
# Display statistics
# ============================================================

def show_statistics(client):
    """
    Show useful statistics from the generated catalog.
    """

    print("\n========== CATALOG STATISTICS ==========")

    total = client.query(
        "SELECT count() FROM tracks"
    ).result_rows[0][0]

    sync_unavailable = client.query(
        """
        SELECT count()
        FROM tracks
        WHERE sync_available = false
        """
    ).result_rows[0][0]

    commercial_disabled = client.query(
        """
        SELECT count()
        FROM tracks
        WHERE commercial_use = false
        """
    ).result_rows[0][0]

    expensive = client.query(
        """
        SELECT count()
        FROM tracks
        WHERE license_price = 2000
        """
    ).result_rows[0][0]

    print(f"Total tracks:          {total}")
    print(f"Sync unavailable:      {sync_unavailable}")
    print(f"Commercial disabled:   {commercial_disabled}")
    print(f"Price = 2000:          {expensive}")

    print("========================================\n")


# ============================================================
# Main
# ============================================================

def main():
    print("🎵 SyncAgent Music Catalog Generator")
    print("------------------------------------")

    # Generate tracks
    tracks = generate_catalog()

    # Connect to ClickHouse
    print("\nConnecting to ClickHouse...")

    client = get_clickhouse_client()

    print("✅ Connected to ClickHouse")

    # Create table
    create_table(client)

    # Insert tracks
    insert_tracks(client, tracks)

    # Show statistics
    show_statistics(client)

    print("🎬 SyncAgent catalog generation complete!")


if __name__ == "__main__":
    main()
