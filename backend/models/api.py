from typing import Optional

from pydantic import BaseModel, Field, model_validator


class AnalyzeRequest(BaseModel):
    """Request model for scene analysis."""

    scene_description: str = Field(
        ...,
        min_length=20,
        description="Text description of the film scene"
    )

    budget: float = Field(
        ...,
        ge=0,
        description="Maximum licensing budget in USD"
    )

    territory: str = Field(
        ...,
        min_length=2,
        description="Required licensing territory"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of recommendations"
    )


class TrackRecommendation(BaseModel):
    """A recommended track that passed pre-clearance validation."""

    track_id: str = Field(
        ...,
        description="Unique catalog track identifier"
    )

    title: str = Field(
        ...,
        description="Track title"
    )

    artist: Optional[str] = Field(
        default=None,
        description="Track artist"
    )

    match_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Creative compatibility score"
    )

    license_cost: Optional[float] = Field(
        default=None,
        ge=0,
        description="License price in USD"
    )

    reason: str = Field(
        ...,
        description="Reason the track fits the scene"
    )

    pre_clearance_status: str = Field(
        ...,
        description="Configured pre-clearance status"
    )


class RejectedTrack(BaseModel):
    """A track rejected during pre-clearance validation."""

    track_id: str = Field(
        ...,
        description="Unique catalog track identifier"
    )
    artist: Optional[str] = Field(
        default=None,
        description="Track artist when available",
    )

    title: str = Field(
        ...,
        description="Track title"
    )

    reason: str = Field(
        ...,
        description="Reason the track was rejected"
    )

    match_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Creative compatibility score, if available"
    )

    @model_validator(mode="before")
    @classmethod
    def convert_old_rejection_format(cls, data):
        """
        Maintain compatibility with the previous agent output:

        {
            "track_id": "...",
            "title": "...",
            "artist": "...",
            "rejection_reasons": [...]
        }

        Convert it into:

        {
            "track_id": "...",
            "title": "...",
            "reason": "..."
        }
        """

        if isinstance(data, dict):

            # New format already has reason.
            if "reason" in data:
                return data

            # Convert old format.
            if "rejection_reasons" in data:

                reasons = data.get(
                    "rejection_reasons",
                    []
                )

                if isinstance(reasons, list):
                    reason = "; ".join(
                        str(item)
                        for item in reasons
                    )

                else:
                    reason = str(reasons)

                converted = {
                    "track_id": data.get("track_id"),
                    "title": data.get("title"),
                    "artist": data.get("artist"),
                    "reason": reason,
                    "match_score": data.get("match_score")
                }

                return converted

        return data


class AnalyzeResponse(BaseModel):
    """Complete SyncAgent analysis response."""

    success: bool = Field(
        ...,
        description="Whether the analysis completed successfully"
    )

    scene_analysis: dict = Field(
        ...,
        description="Structured analysis of the film scene"
    )

    recommendations: list[TrackRecommendation] = Field(
        default_factory=list,
        description="Tracks that passed pre-clearance validation"
    )

    rejected_candidates: list[RejectedTrack] = Field(
        default_factory=list,
        description="Tracks rejected during validation"
    )

    total_candidates: int = Field(
        ...,
        ge=0,
        description="Total number of catalog candidates evaluated"
    )

    disclaimer: str = Field(
        ...,
        description="Licensing disclaimer"
    )
