import os
import random
from pathlib import Path

import clickhouse_connect
from dotenv import load_dotenv

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
    "worldwide",
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
    category = random.choice(["slow", "medium", "fast"])

    if category == "slow":
        return random.randint(55, 80)

    if category == "medium":
        return random.randint(81, 120)

    return random.randint(121, 160)


def generate_energy():
    return random.randint(1, 5)


def generate_duration():
    return random.randint(60, 300)


def generate_title():
    prefix = random.choice(TITLE_PREFIXES)
    word = random.choice(TITLE_WORDS)
    return f"{prefix} {word}"


def generate_track_id(index):
    return f"TRK-{index:04d}"


# ============================================================
# Track generation
# ============================================================

def generate_normal_track(index):
    """
    Generate a valid/licensable track.
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

        "license_price": random.choice([
            100,
            200,
            300,
            500,
            750,
            1000,
        ]),

        "license_type": random.choice(LICENSE_TYPES),
    }


def generate_problematic_track(index):
    """
    Generate a track that SyncAgent should reject.
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
        # Make sure this is different from worldwide.
        track["territory"] = random.choice([
            "india",
            "us",
            "europe",
        ])

    elif problem == "too_expensive":
        track["license_price"] = 2000

    elif problem == "multiple_problems":
        track["sync_available"] = False
        track["commercial_use"] = False
        track["license_price"] = 2000

    return track


def generate_catalog(num_tracks=NUM_TRACKS):
    """
    Generate exactly num_tracks records.

    Approximately 80% are normal.
    Approximately 20% are problematic.
    """

    if num_tracks <= 0:
        raise ValueError("NUM_TRACKS must be greater than 0.")

    normal_count = int(num_tracks * 0.80)
    problematic_count = num_tracks - normal_count

    print(f"Generating {normal_count} normal tracks...")
    print(f"Generating {problematic_count} problematic tracks...")

    tracks = []

    for index in range(1, normal_count + 1):
        tracks.append(generate_normal_track(index))

    for index in range(
        normal_count + 1,
        num_tracks + 1
    ):
        tracks.append(generate_problematic_track(index))

    random.shuffle(tracks)

    return tracks


# ============================================================
# Environment / ClickHouse connection
# ============================================================



def get_clickhouse_client():
    """
    Create a ClickHouse Cloud client.
    """

    BASE_DIR = Path(__file__).resolve().parent.parent
    ENV_FILE = BASE_DIR / ".env"

    load_dotenv(ENV_FILE)


    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST"),
        user=os.getenv("CLICKHOUSE_USER"),
        password=os.getenv("CLICKHOUSE_PASSWORD"),
        secure=True,
    )

    # Verify the connection immediately.
    client.command("SELECT 1")

    return client


# ============================================================
# Database setup
# ============================================================

def create_table(client):
    """
    Create the tracks table if it doesn't exist.
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


def clear_tracks(client):
    """
    Remove ALL existing tracks.

    This is intentionally done before inserting the new catalog.
    """

    print("🗑️ Removing existing tracks...")

    client.command("TRUNCATE TABLE tracks")

    print("✅ Existing tracks removed")


# ============================================================
# Insert tracks
# ============================================================

def insert_tracks(client, tracks):
    """
    Insert generated tracks into ClickHouse.
    """

    if not tracks:
        print("⚠️ No tracks to insert.")
        return

    column_names = [
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
    ]

    rows = [
        [
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
        ]
        for track in tracks
    ]

    client.insert(
        "tracks",
        rows,
        column_names=column_names,
    )

    print(f"✅ Inserted {len(rows)} tracks")


# ============================================================
# Statistics
# ============================================================

def show_statistics(client):
    """
    Display catalog statistics.
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
    BASE_DIR = Path(__file__).resolve().parent.parent
    ENV_FILE = BASE_DIR / ".env"

    load_dotenv(ENV_FILE)
    print("🎵 SyncAgent Music Catalog Generator")
    print("------------------------------------")

    try:
        # ----------------------------------------------------
        # 1. Generate exactly NUM_TRACKS
        # ----------------------------------------------------

        print(f"\nGenerating catalog of {NUM_TRACKS} tracks...")

        tracks = generate_catalog(NUM_TRACKS)

        print(f"✅ Generated {len(tracks)} tracks")

        # ----------------------------------------------------
        # 2. Connect to ClickHouse
        # ----------------------------------------------------

        print("\nConnecting to ClickHouse...")

        client = get_clickhouse_client()

        print("✅ Connected to ClickHouse")

        # ----------------------------------------------------
        # 3. Create table
        # ----------------------------------------------------

        create_table(client)

        # ----------------------------------------------------
        # 4. Delete ALL old tracks
        # ----------------------------------------------------

        clear_tracks(client)

        # ----------------------------------------------------
        # 5. Insert new tracks
        # ----------------------------------------------------

        insert_tracks(client, tracks)

        # ----------------------------------------------------
        # 6. Verify / display statistics
        # ----------------------------------------------------

        show_statistics(client)

        print(
            f"🎬 SyncAgent catalog generation complete! "
            f"{NUM_TRACKS} tracks are now in the database."
        )

    except Exception as e:
        print("\n❌ ERROR")
        print("------------------------------------")
        print(type(e).__name__)
        print(str(e))
        print("------------------------------------")
        raise


if __name__ == "__main__":
    main()
