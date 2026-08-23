from pydantic import BaseModel, Field
from typing import List, Optional


class SceneSchema(BaseModel):
    """
    SceneSchema is a Pydantic model that defines the structure of a scene object.
    It includes various attributes that describe the scene, such as its name, description,
    and other relevant properties.
    """

    mood: List[str] = Field(..., description="List of moods associated with the scene.")

    energy: int = Field(..., ge=1, le=10, description="Energy level of the scene, typically on a scale from 1 to 10.")

    bpm_min: int = Field(..., description="Minimum beats per minute for the scene's music.")

    bpm_max: int = Field(..., description="Maximum beats per minute for the scene's music.")

    genres: List[str] = Field(..., description="List of music genres associated with the scene.")

    instrumentation: Optional[List[str]] = Field(default=None, description="List of instruments used in the scene's music.")
    
    pacing: Optional[str] = Field(default=None, description="Description of the pacing of the scene.")