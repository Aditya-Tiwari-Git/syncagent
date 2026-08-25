"""Services package for SyncAgent.

Provides high-level services for scene analysis, music search, validation, and ranking.
"""

from backend.services.scene_analyzer import analyze_scene
from backend.services.music_search import search_candidate_tracks, get_clickhouse_client
from backend.services.rights_validator import validate_track
from backend.services.ranking import calculate_creative_score, calculate_final_score
from backend.services.sync_pipeline import run_syncagent_pipeline

__all__ = [
    "analyze_scene",
    "search_candidate_tracks",
    "get_clickhouse_client",
    "validate_track",
    "calculate_creative_score",
    "calculate_final_score",
    "run_syncagent_pipeline",
]
