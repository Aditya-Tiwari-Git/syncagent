import os
from dotenv import load_dotenv
load_dotenv(override=True)

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "syncagent-506417"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

from google import genai

print("Project:", os.environ["GOOGLE_CLOUD_PROJECT"])
print("Location:", os.environ["GOOGLE_CLOUD_LOCATION"])
print("Vertex:", os.environ["GOOGLE_GENAI_USE_VERTEXAI"])

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say hello in one short sentence."
)

print("\nMODEL RESPONSE:")
print(response.text)
