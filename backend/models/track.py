"""Data models for music tracks and recommendations."""

from typing import Dict

from pydantic import BaseModel, Field


class Track(BaseModel):
    """A music track in the catalog.
    
    Attributes:
        id: Unique track identifier
        title: Track title
        artist: Artist name
        genre: Primary music genre
        mood: Emotional mood descriptor
        bpm: Tempo in beats per minute
        energy: Energy level (1-10)
        duration_seconds: Track length in seconds
        instrumentation: Comma-separated instrument list
        sync_available: Whether sync rights are available
        commercial_use: Whether commercial use is permitted
        territory: Geographic territory or 'worldwide'
        license_price: Licensing cost in dollars
        license_type: Type of license (e.g., standard_sync, premium_sync)
    """

    id: str = Field(description="Unique track identifier")
    title: str = Field(description="Track title")
    artist: str = Field(description="Artist name")
    genre: str = Field(description="Primary music genre")
    mood: str = Field(description="Emotional mood descriptor")
    bpm: int = Field(ge=1, le=300, description="Tempo in BPM")
    energy: int = Field(ge=1, le=10, description="Energy level 1-10")
    duration_seconds: int = Field(ge=1, description="Track duration in seconds")
    instrumentation: str = Field(description="Comma-separated instruments")
    sync_available: bool = Field(description="Sync rights available")
    commercial_use: bool = Field(description="Commercial use permitted")
    territory: str = Field(description="Territory (worldwide or specific region)")
    license_price: float = Field(ge=0, description="License price in USD")
    license_type: str = Field(description="License type (e.g., standard_sync)")

    model_config = {"str_strip_whitespace": True}


class ValidatedTrack(BaseModel):
    """A track after validation and scoring.
    
    Attributes:
        track: The underlying Track object
        valid: Whether track passed all validation rules
        rejection_reasons: List of reasons track was rejected (if not valid)
        creative_score: Creative fit score (0-100)
        final_score: Final ranking score (0-100)
    """

    track: Track = Field(description="The underlying track")
    valid: bool = Field(description="Passed all validation rules")
    rejection_reasons: list[str] = Field(
        default_factory=list,
        description="Reasons for rejection (if not valid)"
    )
    creative_score: float = Field(
        default=0,
        ge=0,
        le=100,
        description="Creative fit score"
    )
    final_score: float = Field(
        default=0,
        ge=0,
        le=100,
        description="Final ranking score"
    )


class TrackRecommendation(BaseModel):
    """Final recommendation for a track.
    
    Attributes:
        track: The recommended track
        final_score: Overall recommendation score (0-100)
        score_breakdown: Detailed score components
        match_explanation: Human-readable explanation of the match
    """

    track: Track = Field(description="Recommended track")
    final_score: float = Field(
        ge=0,
        le=100,
        description="Overall score"
    )
    score_breakdown: Dict[str, float] = Field(
        description="Breakdown of score components"
    )
    match_explanation: str = Field(
        description="Explanation of why this track is recommended"
    )

class TrackData(BaseModel):
    """Complete catalog track data required for rights validation."""

    id: str = Field(description="Unique catalog track ID")
    title: str = Field(description="Track title")
    artist: str = Field(description="Artist name")
    genre: str = Field(description="Primary genre")
    mood: str = Field(description="Primary mood")
    bpm: int = Field(description="Tempo in BPM")
    energy: int = Field(description="Energy level from 1 to 10")
    duration_seconds: int = Field(description="Track duration in seconds")
    instrumentation: str = Field(
        description="Comma-separated instruments, e.g. 'piano, cello, synth'"
    )
    sync_available: bool = Field(description="Whether sync licensing is available")
    commercial_use: bool = Field(description="Whether commercial use is permitted")
    territory: str = Field(description="Licensed territory, e.g. 'worldwide'")
    license_price: float = Field(description="License price in USD")
    license_type: str = Field(description="License type, e.g. 'standard_sync'")
    