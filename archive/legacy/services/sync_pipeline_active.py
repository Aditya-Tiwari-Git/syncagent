"""Main SyncAgent orchestration pipeline.

Coordinates scene analysis, music search, validation, and ranking.
"""

from typing import Any, Dict, List

from backend.services.scene_analyzer import analyze_scene
from backend.services.music_search import search_candidate_tracks
from backend.services.rights_validator import validate_track
from backend.services.ranking import (
    calculate_creative_score,
    calculate_final_score,
)

def run_syncagent_pipeline(
    scene: str,
    budget: float,
    territory: str,
) -> Dict[str, Any]:
    """Execute the complete SyncAgent music synchronization pipeline.
    
    This orchestrates the full workflow:
    1. Analyzes the scene using Gemini AI to extract music requirements
    2. Searches ClickHouse for candidate tracks within BPM range
    3. Validates tracks for licensing, rights, budget, and territory
    4. Ranks valid tracks using creative + budget scoring
    5. Returns recommendations and rejection reasons
    
    Args:
        scene: Text description of the film scene
        budget: Maximum licensing budget in USD
        territory: Target territory (e.g., 'worldwide', 'india')
        
    Returns:
        Dictionary with keys:
        - requirements: SceneRequirements object
        - recommendations: List of ValidatedTrack sorted by final score
        - rejected: List of ValidatedTrack objects that failed validation
        
    Raises:
        ValueError: If scene, budget, or territory are invalid
        Exception: If Gemini, ClickHouse, or other services fail
        
    Example:
        >>> result = run_syncagent_pipeline(
        ...     scene="A tense chase scene",
        ...     budget=1000,
        ...     territory="worldwide"
        ... )
        >>> print(f"Found {len(result['recommendations'])} recommendations")
        >>> for track in result["recommendations"][:3]:
        ...     print(f"{track.track.title} - Score: {track.final_score}")
    """
    # Input validation
    if not scene or not scene.strip():
        raise ValueError("Scene description cannot be empty")
    
    if budget <= 0:
        raise ValueError("Budget must be positive")
    
    if not territory or not territory.strip():
        raise ValueError("Territory cannot be empty")
    
    # Step 1: Scene Analysis
    try:
        requirements = analyze_scene(scene)
    except Exception:
        raise
    
    # Step 2: Music Search
    try:
        candidates = search_candidate_tracks(requirements)
    except Exception:
        raise
    
    # Step 3 & 4: Validation and Ranking
    valid_tracks: List = []
    rejected_tracks: List = []
    
    for track in candidates:
        try:
            validation = validate_track(
                track=track,
                budget=budget,
                territory=territory,
            )
            
            if validation.valid:
                # Calculate scores for valid tracks
                creative_score = calculate_creative_score(
                    track=track,
                    requirements=requirements,
                )
                
                final_score = calculate_final_score(
                    creative_score=creative_score,
                    track=track,
                    budget=budget,
                )
                
                validation.creative_score = creative_score
                validation.final_score = final_score
                
                valid_tracks.append(validation)
            else:
                rejected_tracks.append(validation)
        except Exception:
            continue
    
    # Sort valid tracks by final score
    ranked_tracks = sorted(
        valid_tracks,
        key=lambda x: x.final_score,
        reverse=True,
    )
    
    return {
        "requirements": requirements,
        "recommendations": ranked_tracks,
        "rejected": rejected_tracks,
    }
