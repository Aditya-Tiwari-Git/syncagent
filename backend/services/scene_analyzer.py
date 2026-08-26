"""Scene analysis service using Google Gemini AI.

Analyzes film scenes to extract structured musical requirements.
"""

import json
import re

from google import genai
from google.genai.types import HttpOptions

from backend.config import settings
from backend.models.scene import SceneRequirements

def analyze_scene(scene_description: str) -> SceneRequirements:
    """Analyze a film scene using Gemini AI to extract music requirements.
    
    Uses Google's Gemini 2.5 Flash model to understand the emotional and 
    pacing context of a scene and extract structured musical requirements.
    
    Args:
        scene_description: Text description of the film scene
        
    Returns:
        SceneRequirements: Structured music requirements for the scene
        
    Raises:
        ValueError: If scene description is empty
        json.JSONDecodeError: If Gemini returns invalid JSON
        Exception: If Google Cloud credentials are missing or invalid
        
    Example:
        >>> scene = "A tense chase through a dark alley at night"
        >>> reqs = analyze_scene(scene)
        >>> print(reqs.energy, reqs.pacing)
        4 fast
    """
    if not scene_description or not scene_description.strip():
        raise ValueError("Scene description cannot be empty")
    
    try:
        client = genai.Client(
            vertexai=True,
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_LOCATION,
            http_options=HttpOptions(api_version="v1")
        )
    except Exception:
        raise

    prompt = f"""You are an expert film music supervisor.

Analyze the following film scene and determine the ideal musical characteristics.

SCENE:

{scene_description}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "mood": ["string"],
    "energy": 1,
    "bpm_min": 60,
    "bpm_max": 80,
    "genres": ["string"],
    "instrumentation": ["string"],
    "pacing": "string",
    "scene_duration_seconds": 90
}}

RULES:

1. mood must contain 1 to 3 lowercase mood words.
2. energy must be an integer from 1 to 5.
3. bpm_min must be lower than bpm_max.
4. bpm values must be realistic (40-220 BPM).
5. genres must contain 1 to 3 values.
6. instrumentation must contain suitable instruments.
7. pacing must be one of: slow, medium, fast
8. scene_duration_seconds should be your reasonable estimate of the scene duration.

Do not include markdown.
Do not include explanations.
Return JSON only.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
    except Exception:
        raise

    text = response.text.strip()

    # Remove Markdown code fences if Gemini adds them
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise

    try:
        requirements = SceneRequirements(**data)
        return requirements
    except Exception:
        raise