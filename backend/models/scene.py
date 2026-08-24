from typing import Literal

from pydantic import BaseModel, Field, model_validator

class SceneRequirements(BaseModel):
    """Structured musical requirements extracted from a film scene."""

    mood: list[str] = Field(..., min_length=1, max_length=3)

    energy: int = Field(..., ge=1, le=5)

    bpm_min: int = Field(..., ge=1, le=300)

    bpm_max: int = Field(..., ge=1, le=300)

    genres: list[str] = Field(..., min_length=1, max_length=3)

    instrumentation: list[str] = Field(default_factory=list)

    pacing: Literal["slow", "medium", "fast"]

    @model_validator(mode="after")
    def validate_bpm_range(self) -> "SceneRequirements":
        """Ensure the tempo range is ordered."""
        if self.bpm_min >= self.bpm_max:
            raise ValueError("bpm_min must be less than bpm_max")
        return self