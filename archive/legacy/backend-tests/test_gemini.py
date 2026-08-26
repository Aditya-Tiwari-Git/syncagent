import os

from google import genai
from google.genai.types import HttpOptions, GenerateContentConfig
from backend.services.scene_schema import SceneSchema

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
    http_options=HttpOptions(api_version="v1"),
)

prompt = """
Analyze the following film scene.

Scene:
A man walks alone through an empty city at night
after a painful breakup.

Return a concise analysis of:
- mood
- energy
- pacing
- suggested music genre
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=GenerateContentConfig(
        response_mime_type = "application/json",
        response_schema = SceneSchema)
)

print(response.text)
