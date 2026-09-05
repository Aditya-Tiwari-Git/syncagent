"""Seed the SyncAgent ClickHouse catalog with deterministic and generated tracks.

Safe defaults:
- The table is created if needed.
- Existing rows are preserved.
- Existing IDs are skipped to make repeated runs idempotent.
- Use --clear explicitly when replacing the catalog.

Examples:
    python database/seed_catalog.py
    python database/seed_catalog.py --count 200 --seed 42
    python database/seed_catalog.py --clear --count 200 --seed 42
    python database/seed_catalog.py --append --count 50 --seed 7
"""

from __future__ import annotations

import argparse
import os
import random
from pathlib import Path
from typing import Any

import clickhouse_connect
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

COLUMNS = [
    "id", "title", "artist", "genre", "mood", "bpm", "energy",
    "duration_seconds", "instrumentation", "sync_available", "commercial_use",
    "territory", "license_price", "license_type",
]

DEMO_TRACKS: list[dict[str, Any]] = [
    {"id": "TRK-DEMO-001", "title": "Midnight Mumbai", "artist": "Alex Morgan", "genre": "cinematic", "mood": "dark, melancholic, introspective", "bpm": 68, "energy": 2, "duration_seconds": 152, "instrumentation": "piano, strings, ambient pads", "sync_available": True, "commercial_use": True, "territory": "worldwide", "license_price": 500.0, "license_type": "standard_sync"},
    {"id": "TRK-DEMO-002", "title": "Rain on Marine Drive", "artist": "Luna Fields", "genre": "ambient", "mood": "melancholic, peaceful, urban", "bpm": 62, "energy": 1, "duration_seconds": 178, "instrumentation": "piano, soft synth", "sync_available": True, "commercial_use": True, "territory": "worldwide", "license_price": 350.0, "license_type": "indie_sync"},
    {"id": "TRK-DEMO-003", "title": "Last Case", "artist": "The Midnight Ensemble", "genre": "cinematic", "mood": "dark, suspenseful, tense", "bpm": 70, "energy": 2, "duration_seconds": 164, "instrumentation": "cello, piano, strings", "sync_available": True, "commercial_use": True, "territory": "worldwide", "license_price": 1800.0, "license_type": "premium_sync"},
    {"id": "TRK-DEMO-004", "title": "City After Dark", "artist": "Nova Sound", "genre": "electronic", "mood": "dark, urban, melancholic", "bpm": 76, "energy": 2, "duration_seconds": 142, "instrumentation": "synth, ambient pads", "sync_available": False, "commercial_use": True, "territory": "worldwide", "license_price": 400.0, "license_type": "standard_sync"},
    {"id": "TRK-DEMO-005", "title": "Neon Chase", "artist": "Echo Theory", "genre": "electronic", "mood": "tense, energetic, suspenseful", "bpm": 148, "energy": 5, "duration_seconds": 126, "instrumentation": "synth, drums, brass", "sync_available": True, "commercial_use": True, "territory": "worldwide", "license_price": 700.0, "license_type": "standard_sync"},
    {"id": "TRK-DEMO-006", "title": "First Light", "artist": "Maya Rivers", "genre": "orchestral", "mood": "hopeful, peaceful, uplifting", "bpm": 82, "energy": 3, "duration_seconds": 190, "instrumentation": "strings, piano, orchestra", "sync_available": True, "commercial_use": True, "territory": "worldwide", "license_price": 600.0, "license_type": "standard_sync"},
    {"id": "TRK-DEMO-007", "title": "Summer Streets", "artist": "Aria Collective", "genre": "acoustic", "mood": "happy, hopeful, energetic", "bpm": 116, "energy": 4, "duration_seconds": 138, "instrumentation": "acoustic guitar, percussion", "sync_available": True, "commercial_use": True, "territory": "worldwide", "license_price": 300.0, "license_type": "indie_sync"},
    {"id": "TRK-DEMO-008", "title": "Broken Silence", "artist": "Daniel Stone", "genre": "ambient", "mood": "sad, melancholic, emotional", "bpm": 58, "energy": 1, "duration_seconds": 205, "instrumentation": "piano, cello", "sync_available": True, "commercial_use": False, "territory": "worldwide", "license_price": 250.0, "license_type": "sync_demo"},
    {"id": "TRK-DEMO-009", "title": "After Goodbye", "artist": "Silver Frame", "genre": "cinematic", "mood": "romantic, sad, melancholic", "bpm": 74, "energy": 2, "duration_seconds": 171, "instrumentation": "piano, strings, guitar", "sync_available": True, "commercial_use": True, "territory": "us", "license_price": 450.0, "license_type": "standard_sync"},
    {"id": "TRK-DEMO-010", "title": "Hidden Evidence", "artist": "Northbound", "genre": "suspense", "mood": "suspenseful, dark, tense", "bpm": 88, "energy": 3, "duration_seconds": 132, "instrumentation": "strings, synth, percussion", "sync_available": False, "commercial_use": False, "territory": "us", "license_price": 2200.0, "license_type": "premium_sync"},
    {"id": "TRK-DEMO-011", "title": "Wedding Lanterns", "artist": "Velvet Signal", "genre": "orchestral", "mood": "romantic, happy, hopeful", "bpm": 96, "energy": 3, "duration_seconds": 210, "instrumentation": "piano, orchestra, strings", "sync_available": True, "commercial_use": True, "territory": "worldwide", "license_price": 800.0, "license_type": "standard_sync"},
    {"id": "TRK-DEMO-012", "title": "Victory Lap", "artist": "Aria Collective", "genre": "electronic", "mood": "happy, energetic, hopeful", "bpm": 132, "energy": 5, "duration_seconds": 118, "instrumentation": "synth, drums, brass", "sync_available": True, "commercial_use": True, "territory": "worldwide", "license_price": 1000.0, "license_type": "premium_sync"},
    {"id": "TRK-DEMO-013", "title": "Quiet Room", "artist": "Luna Fields", "genre": "ambient", "mood": "peaceful, introspective, calm", "bpm": 52, "energy": 1, "duration_seconds": 240, "instrumentation": "piano, ambient pads", "sync_available": True, "commercial_use": True, "territory": "india", "license_price": 150.0, "license_type": "indie_sync"},
    {"id": "TRK-DEMO-014", "title": "Blue Note Memory", "artist": "Alex Morgan", "genre": "jazz", "mood": "romantic, peaceful, nostalgic", "bpm": 92, "energy": 2, "duration_seconds": 186, "instrumentation": "piano, saxophone, upright bass", "sync_available": True, "commercial_use": True, "territory": "europe", "license_price": 400.0, "license_type": "standard_sync"},
    {"id": "TRK-DEMO-015", "title": "Nocturne Contract", "artist": "Northbound", "genre": "cinematic", "mood": "dark, melancholic, suspenseful", "bpm": 66, "energy": 2, "duration_seconds": 160, "instrumentation": "piano, strings", "sync_available": False, "commercial_use": False, "territory": "india", "license_price": 2000.0, "license_type": "premium_sync"},
]

STYLE_PROFILES = [
    ("cinematic", "dark", 68, 2, "piano, strings"),
    ("ambient", "peaceful", 60, 1, "piano, ambient pads"),
    ("orchestral", "hopeful", 88, 3, "strings, orchestra"),
    ("electronic", "energetic", 132, 5, "synth, drums"),
    ("acoustic", "happy", 108, 4, "acoustic guitar, percussion"),
    ("jazz", "romantic", 94, 2, "piano, saxophone"),
    ("suspense", "tense", 102, 4, "strings, percussion"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=500, help="Total records including deterministic demos.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible generated records.")
    parser.add_argument("--clear", action="store_true", help="Explicitly truncate tracks before inserting.")
    parser.add_argument("--append", action="store_true", help="Append new records; existing IDs are skipped.")
    return parser


def generate_random_tracks(count: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    tracks = []
    for index in range(count):
        genre, mood, bpm, energy, instrumentation = rng.choice(STYLE_PROFILES)
        tracks.append({
            "id": f"TRK-GEN-{seed:03d}-{index + 1:04d}",
            "title": f"{mood.title()} {genre.title()} {index + 1}",
            "artist": rng.choice(["Demo Artist", "Northbound", "Maya Rivers", "Echo Theory", "Silver Frame"]),
            "genre": genre,
            "mood": mood,
            "bpm": max(40, min(220, bpm + rng.randint(-8, 8))),
            "energy": max(1, min(5, energy + rng.choice([-1, 0, 0, 1]))),
            "duration_seconds": rng.randint(90, 240),
            "instrumentation": instrumentation,
            "sync_available": rng.random() > 0.08,
            "commercial_use": rng.random() > 0.1,
            "territory": rng.choice(["worldwide", "india", "us", "europe"]),
            "license_price": rng.choice([100.0, 200.0, 300.0, 500.0, 750.0, 1000.0, 1500.0]),
            "license_type": rng.choice(["standard_sync", "indie_sync", "premium_sync"]),
        })
    return tracks


def build_catalog(count: int, seed: int) -> list[dict[str, Any]]:
    if count < len(DEMO_TRACKS):
        raise ValueError(f"--count must be at least {len(DEMO_TRACKS)} to preserve demo cases")
    return DEMO_TRACKS + generate_random_tracks(count - len(DEMO_TRACKS), seed)


def create_client():
    required = ["CLICKHOUSE_HOST", "CLICKHOUSE_USER", "CLICKHOUSE_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing ClickHouse configuration: {', '.join(missing)}")
    return clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_HOST"],
        port=int(os.getenv("CLICKHOUSE_PORT", "8443")),
        database=os.getenv("CLICKHOUSE_DATABASE", "default"),
        username=os.environ["CLICKHOUSE_USER"],
        password=os.environ["CLICKHOUSE_PASSWORD"],
        secure=True,
    )


def create_table(client) -> None:
    schema = (PROJECT_ROOT / "database" / "schema.sql").read_text(encoding="utf-8")
    client.command(schema)


def existing_ids(client) -> set[str]:
    return {row[0] for row in client.query("SELECT id FROM tracks").result_rows}


def insert_tracks(client, tracks: list[dict[str, Any]]) -> int:
    if not tracks:
        return 0
    rows = [[track[column] for column in COLUMNS] for track in tracks]
    client.insert("tracks", rows, column_names=COLUMNS)
    return len(rows)


def main() -> None:
    args = build_parser().parse_args()
    if args.clear and args.append:
        raise SystemExit("Use either --clear or --append, not both.")
    catalog = build_catalog(args.count, args.seed)
    client = create_client()
    create_table(client)
    if args.clear:
        client.command("TRUNCATE TABLE tracks")
        candidates = catalog
    else:
        ids = existing_ids(client)
        candidates = [track for track in catalog if track["id"] not in ids]
    inserted = insert_tracks(client, candidates)
    print(f"Catalog ready: {inserted} inserted, {len(catalog) - inserted} already present.")
    print(f"Deterministic demo tracks: {len(DEMO_TRACKS)}; total requested: {len(catalog)}.")


if __name__ == "__main__":
    main()
