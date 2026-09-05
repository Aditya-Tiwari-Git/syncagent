from typing import Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request model for scene analysis."""

    scene_description: str = Field(
        ...,
        min_length=1,
        description="Text description of the film scene"
    )

    budget: float = Field(
        ...,
        gt=0,
        description="Maximum licensing budget in USD"
    )

    territory: str = Field(
        ...,
        min_length=1,
        description="Required licensing territory"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Maximum number of recommendations"
    )


class TrackRecommendation(BaseModel):
    """A recommended track that passed pre-clearance checks."""

    track_id: str = Field(
        ...,
        description="Unique identifier of the track"
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

    license_cost: float = Field(
        ...,
        ge=0,
        description="License price in USD"
    )

    reason: str = Field(
        ...,
        description="Reason why the track fits the scene"
    )

    pre_clearance_status: Optional[str] = Field(
        default=None,
        description="Configured pre-clearance status"
    )


class RejectedTrack(BaseModel):
    """A track that failed one or more pre-clearance checks."""

    track_id: str = Field(
        ...,
        description="Unique identifier of the track"
    )

    title: str = Field(
        ...,
        description="Track title"
    )

    artist: Optional[str] = Field(
        default=None,
        description="Track artist"
    )

    rejection_reasons: list[str] = Field(
        default_factory=list,
        description="Reasons why the track was rejected"
    )


class AnalyzeResponse(BaseModel):
    """Response model for SyncAgent analysis."""

    success: bool = Field(
        ...,
        description="Whether the analysis completed successfully"
    )

    scene_analysis: dict = Field(
        default_factory=dict,
        description="Structured analysis of the film scene"
    )

    recommendations: list[TrackRecommendation] = Field(
        default_factory=list,
        description="Tracks that passed pre-clearance checks"
    )

    rejected_candidates: list[RejectedTrack] = Field(
        default_factory=list,
        description="Tracks rejected during validation"
    )

    total_candidates: int = Field(
        ...,
        ge=0,
        description="Total number of candidates evaluated"
    )

    disclaimer: str = Field(
        default=(
            "Final licensing must be verified with "
            "the relevant rights holder."
        ),
        description="Licensing disclaimer"
    )
