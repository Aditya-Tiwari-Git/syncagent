import json
import re
import uuid

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from backend.agents.root_agent import root_agent
from backend.models.api import AnalyzeResponse
from backend.services.logger import logger


APP_NAME = "syncagent"


def clean_json_response(response: str) -> str:
    """
    Clean common formatting added by the model before JSON parsing.
    """

    if not response:
        raise ValueError(
            "SyncAgent returned an empty response"
        )

    cleaned = response.strip()

    # Remove Markdown code fences if the model ignores instructions.
    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()

    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    # Sometimes the model may accidentally return text around JSON.
    # First try the cleaned response directly.
    try:
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError:
        pass

    # Try extracting the outermost JSON object.
    match = re.search(
        r"\{.*\}",
        cleaned,
        re.DOTALL
    )

    if match:
        extracted = match.group(0).strip()

        try:
            json.loads(extracted)
            return extracted
        except json.JSONDecodeError:
            pass

    return cleaned


async def run_syncagent(
    scene_description: str,
    budget: float,
    territory: str,
    top_k: int = 5
):
    """
    Run the SyncAgent ADK workflow and return parsed JSON.
    """

    workflow_id = str(uuid.uuid4())

    logger.info(
        "[%s] Starting SyncAgent workflow",
        workflow_id
    )

    user_id = f"user-{uuid.uuid4()}"
    session_id = f"session-{uuid.uuid4()}"

    try:

        session_service = InMemorySessionService()

        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )

        prompt = f"""
Analyze the following film scene and find suitable
music candidates.

SCENE:
{scene_description}

BUDGET:
${budget}

TERRITORY:
{territory}

Return at most {top_k} recommendations.

Follow all SyncAgent pre-clearance rules.

Do not claim legal clearance.

IMPORTANT OUTPUT RULES:

Return ONLY valid JSON.

Do not use Markdown.

Do not use ```json fences.

Do not put any text before or after the JSON.

The response MUST use exactly this structure:

{{
  "scene_analysis": {{
    "mood": [],
    "energy": 0,
    "bpm_min": 0,
    "bpm_max": 0,
    "genres": [],
    "instrumentation": [],
    "pacing": "",
    "scene_duration_seconds": 0
  }},

  "recommendations": [],

  "rejected_candidates": [],

  "total_candidates": 0,

  "disclaimer": "Final licensing must be verified with the relevant rights holder."
}}

Recommendation objects MUST contain:

- track_id
- title
- artist
- match_score
- license_cost
- reason
- pre_clearance_status

Rejected candidate objects MUST contain:

- track_id
- title
- artist
- rejection_reasons

Only recommend candidates that passed the deterministic
rights validation tool.

Never invent track information.

Never invent pricing.

Never invent licensing rights.

Never claim legal clearance.
"""

        message = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=prompt
                )
            ]
        )

        final_response = ""

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):

            if (
                event.is_final_response()
                and event.content
            ):

                for part in event.content.parts:

                    if part.text:
                        final_response += part.text

        logger.info(
            "[%s] Agent response received",
            workflow_id
        )

        print("\n===== RAW AGENT RESPONSE =====")
        print(final_response)
        print("================================\n")

        cleaned_response = clean_json_response(
            final_response
        )

        try:

            parsed = json.loads(
                cleaned_response
            )

        except json.JSONDecodeError as e:

            logger.error(
                "[%s] Agent returned invalid JSON",
                workflow_id
            )

            print("\n===== FAILED JSON =====")
            print(cleaned_response)
            print("=======================\n")

            raise ValueError(
                f"SyncAgent returned invalid JSON: {e}"
            ) from e

        logger.info(
            "[%s] SyncAgent workflow completed",
            workflow_id
        )

        validated = AnalyzeResponse.model_validate(
            {
                "success": True,
                **parsed,
            }
        )

        return validated.model_dump()

    except Exception:

        logger.exception(
            "[%s] SyncAgent workflow failed",
            workflow_id
        )

        raise
