import json
import re

from google import genai
from google.genai.types import HttpOptions

from backend.config import settings
from backend.models.scene import SceneRequirements


def analyze_scene(scene_description: str) -> SceneRequirements:
    """
    Uses Gemini to analyze a film scene and extract
    structured music requirements.
    """

    client = genai.Client(
        vertexai=True,
        project=settings.GOOGLE_CLOUD_PROJECT,
        location=settings.GOOGLE_CLOUD_LOCATION,
        http_options=HttpOptions(api_version="v1")
    )

    prompt = f"""
You are an expert film music supervisor.

Analyze the following film scene and determine the
ideal musical characteristics.

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
    "pacing": "string"
}}

RULES:

1. mood must contain 1 to 3 lowercase mood words.
2. energy must be an integer from 1 to 5.
3. bpm_min and bpm_max must be realistic.
4. bpm_min must be less than bpm_max.
5. genres should contain 1 to 3 genres.
6. instrumentation should contain suitable instruments.
7. pacing should be one of:
   slow
   medium
   fast

Do not include markdown.
Do not include explanations.
Return JSON only.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = response.text.strip()

    # Remove Markdown code fences if Gemini adds them
    text = re.sub(
        r"^```json\s*",
        "",
        text
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    data = json.loads(text)

    return SceneRequirements(**data)