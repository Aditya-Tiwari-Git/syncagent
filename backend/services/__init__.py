"""Services package for SyncAgent.

Provides high-level services for scene analysis, music search, validation, and ranking.
"""

from backend.services.scene_analyzer import analyze_scene
from backend.services.music_search import search_candidate_tracks, get_clickhouse_client
from backend.services.rights_validator import validate_track

__all__ = [
    "analyze_scene",
    "search_candidate_tracks",
    "get_clickhouse_client",
    "validate_track",
]
