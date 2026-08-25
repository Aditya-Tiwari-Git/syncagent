"""Data models for scene analysis results."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SceneRequirements(BaseModel):
    """Structured musical requirements extracted from a film scene.
    
    Attributes:
        mood: List of emotional tones (1-3 values)
        energy: Energy level from 1 (calm) to 5 (intense)
        bpm_min: Minimum tempo in beats per minute
        bpm_max: Maximum tempo in beats per minute
        genres: Musical genres suitable for the scene (1-3 values)
        instrumentation: Instrument types to feature (1+ values)
        pacing: Overall pacing of the scene (slow/medium/fast)
        scene_duration_seconds: Estimated scene duration in seconds
    """

    mood: list[str] = Field(
        min_length=1,
        max_length=3,
        description="Desired emotional moods (1-3)"
    )

    energy: int = Field(
        ge=1,
        le=5,
        description="Energy level (1=calm, 5=intense)"
    )

    bpm_min: int = Field(
        ge=40,
        le=220,
        description="Minimum tempo in BPM"
    )

    bpm_max: int = Field(
        ge=40,
        le=220,
        description="Maximum tempo in BPM"
    )

    genres: list[str] = Field(
        min_length=1,
        max_length=3,
        description="Musical genres (1-3)"
    )

    instrumentation: list[str] = Field(
        min_length=1,
        description="Instrument types to feature"
    )

    pacing: Literal["slow", "medium", "fast"] = Field(
        description="Scene pacing classification"
    )

    scene_duration_seconds: int = Field(
        default=90,
        ge=1,
        le=600,
        description="Estimated scene duration in seconds"
    )

    @model_validator(mode="after")
    def validate_bpm_range(self) -> "SceneRequirements":
        """Ensure the tempo range is ordered correctly.
        
        Raises:
            ValueError: If bpm_min >= bpm_max
        """
        if self.bpm_min >= self.bpm_max:
            raise ValueError(
                f"bpm_min ({self.bpm_min}) must be less than bpm_max ({self.bpm_max})"
            )
        return self