from pydantic import BaseModel, Field


class Track(BaseModel):
    id: str
    title: str
    artist: str

    genre: str
    mood: str

    bpm: int
    energy: int
    duration_seconds: int

    instrumentation: str

    sync_available: bool
    commercial_use: bool

    territory: str

    license_price: float
    license_type: str

class ValidatedTrack(BaseModel):
    track: Track

    valid: bool

    rejection_reasons: list[str] = Field(default_factory=list)

    creative_score: float = 0
    final_score: float = 0
    