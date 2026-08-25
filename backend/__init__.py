"""Backend package for SyncAgent.

Provides scene analysis, music search, validation, and ranking services.
"""

from backend.config import settings, Settings
from backend.models.scene import SceneRequirements
from backend.models.track import Track, ValidatedTrack, TrackRecommendation
from backend.services.scene_analyzer import analyze_scene
from backend.services.music_search import search_candidate_tracks
from backend.services.rights_validator import validate_track
from backend.services.ranking import calculate_creative_score, calculate_final_score
from backend.services.sync_pipeline import run_syncagent_pipeline

__all__ = [
    # Config
    "settings",
    "Settings",
    # Models
    "SceneRequirements",
    "Track",
    "ValidatedTrack",
    "TrackRecommendation",
    # Services
    "analyze_scene",
    "search_candidate_tracks",
    "validate_track",
    "calculate_creative_score",
    "calculate_final_score",
    "run_syncagent_pipeline",
]
