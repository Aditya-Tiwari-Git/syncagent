"""Track ranking and scoring service.

Calculates creative fit and budget-adjusted final scores for tracks.
"""

import logging
from typing import Dict

from backend.models.scene import SceneRequirements
from backend.models.track import Track

logger = logging.getLogger(__name__)


def calculate_creative_score(
    track: Track,
    requirements: SceneRequirements
) -> float:
    """Calculate creative fit score for a track against scene requirements.
    
    Scoring breakdown (100 points total):
    - Mood match (40 points): Track mood matches any in requirements
    - BPM fit (20 points): Track BPM within required range
    - Genre fit (15 points): Track genre in requirements list
    - Energy match (15 points): Based on energy difference
      * Exact match (0 difference): 15 points
      * 1 level difference: 10 points
      * 2 level difference: 5 points
    - Instrumentation (10 points): If any instruments match
    
    Args:
        track: Track to score
        requirements: Scene requirements to score against
        
    Returns:
        Creative score (0-100)
        
    Example:
        >>> score = calculate_creative_score(track, requirements)
        >>> print(f"Creative score: {score}/100")
        Creative score: 85.0/100
    """
    score = 0.0
    breakdown: Dict[str, float] = {}
    
    # -------------------------
    # MOOD (Weight: 40 points)
    # -------------------------
    track_mood = track.mood.lower()
    if track_mood in requirements.mood:
        score += 40
        breakdown["mood"] = 40
        logger.debug(f"Track {track.id}: mood '{track_mood}' matched")
    else:
        breakdown["mood"] = 0
    
    # -------------------------
    # BPM (Weight: 20 points)
    # -------------------------
    if (
        requirements.bpm_min
        <= track.bpm
        <= requirements.bpm_max
    ):
        score += 20
        breakdown["bpm"] = 20
        logger.debug(f"Track {track.id}: BPM {track.bpm} within range")
    else:
        breakdown["bpm"] = 0
    
    # -------------------------
    # GENRE (Weight: 15 points)
    # -------------------------
    if track.genre.lower() in requirements.genres:
        score += 15
        breakdown["genre"] = 15
        logger.debug(f"Track {track.id}: genre '{track.genre}' matched")
    else:
        breakdown["genre"] = 0
    
    # -------------------------
    # ENERGY (Weight: 15 points)
    # -------------------------
    energy_difference = abs(track.energy - requirements.energy)
    if energy_difference == 0:
        score += 15
        breakdown["energy"] = 15
    elif energy_difference == 1:
        score += 10
        breakdown["energy"] = 10
    elif energy_difference == 2:
        score += 5
        breakdown["energy"] = 5
    else:
        breakdown["energy"] = 0
    
    logger.debug(f"Track {track.id}: energy difference {energy_difference}, score +{breakdown['energy']}")
    
    # -------------------------
    # INSTRUMENTATION (Weight: 10 points)
    # -------------------------
    track_instruments = [
        item.strip().lower()
        for item in track.instrumentation.split(",")
    ]
    
    matching_instruments = set(
        track_instruments
    ).intersection(
        set(requirements.instrumentation)
    )
    
    if matching_instruments:
        score += 10
        breakdown["instrumentation"] = 10
        logger.debug(f"Track {track.id}: instruments matched {matching_instruments}")
    else:
        breakdown["instrumentation"] = 0
    
    final_score = round(score, 2)
    logger.info(f"Track {track.id}: creative score = {final_score}")
    
    return final_score


def calculate_final_score(
    creative_score: float,
    track: Track,
    budget: float
) -> float:
    """Calculate final ranking score combining creative fit and budget factors.
    
    Formula:
    - Start with creative score (0-100)
    - Add budget bonus:
      * +5 points if price <= 50% of budget
      * +2 points if price <= 75% of budget
    - Cap at 100 points
    
    Args:
        creative_score: Creative fit score from calculate_creative_score
        track: Track being scored
        budget: Total budget in USD
        
    Returns:
        Final score (0-100)
        
    Example:
        >>> final = calculate_final_score(85.0, track, 500)
        >>> print(f"Final score: {final}")
        Final score: 90.0
    """
    score = creative_score
    budget_bonus = 0
    
    # Budget-based bonuses
    if track.license_price <= budget * 0.5:
        score += 5
        budget_bonus = 5
        logger.debug(
            f"Track {track.id}: budget bonus +5 (price {track.license_price} <= {budget * 0.5})"
        )
    elif track.license_price <= budget * 0.75:
        score += 2
        budget_bonus = 2
        logger.debug(
            f"Track {track.id}: budget bonus +2 (price {track.license_price} <= {budget * 0.75})"
        )
    
    final = round(min(score, 100), 2)
    logger.info(
        f"Track {track.id}: final score = {final} "
        f"(creative={creative_score}, budget_bonus={budget_bonus})"
    )
    
    return final
