import json
import os
import re
import uuid

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from backend.agents.root_agent import root_agent
from backend.models.api import AnalyzeResponse
from backend.models.scene import SceneRequirements
from backend.services.matching import calculate_match_score
from backend.services.music_search import search_candidate_tracks
from backend.services.recommendations import (
    create_recommendation,
    generate_match_explanation,
)
from backend.services.rights_validator import validate_track
from backend.services.scene_analyzer import analyze_scene
from backend.services.logger import logger


APP_NAME = "syncagent"
DISCLAIMER = "Final licensing must be verified with the relevant rights holder."


def build_catalog_result(
    scene_analysis: dict,
    budget: float,
    territory: str,
    top_k: int,
) -> dict:
    """Build recommendations from authoritative catalog and rules data.

    Gemini supplies scene interpretation, but it never decides licensing or
    scores. This function evaluates every catalog candidate deterministically.
    """
    requirements = SceneRequirements(
        mood=list(scene_analysis.get("mood", []))[:3] or ["cinematic"],
        energy=int(scene_analysis.get("energy", 3)),
        bpm_min=int(scene_analysis.get("bpm_min", 60)),
        bpm_max=int(scene_analysis.get("bpm_max", 80)),
        genres=list(scene_analysis.get("genres", []))[:3] or ["cinematic"],
        instrumentation=list(scene_analysis.get("instrumentation", [])) or ["piano"],
        pacing=scene_analysis.get("pacing", "medium"),
        scene_duration_seconds=int(scene_analysis.get("scene_duration_seconds", 90)),
    )
    candidates = search_candidate_tracks(requirements, limit=500)
    rejected = []
    passing = []
    for track in candidates:
        validation = validate_track(track, budget, territory)
        creative_score = calculate_match_score(track, requirements)["final_score"]
        if validation.valid:
            passing.append(track)
        else:
            rejected.append({
                "track_id": track.id,
                "title": track.title,
                "artist": track.artist,
                "reason": "; ".join(validation.rejection_reasons),
                "match_score": creative_score,
            })

    # Rights-passing tracks remain eligible even when creative fit is weak;
    # hiding every valid license behind a score threshold creates a false
    # no-match result. The score is still shown transparently to the user.
    ranked = sorted(
        (create_recommendation(track, requirements) for track in passing),
        key=lambda item: item.final_score,
        reverse=True,
    )
    recommendations = [
        {
            "track_id": item.track.id,
            "title": item.track.title,
            "artist": item.track.artist,
            "match_score": item.final_score,
            "license_cost": item.track.license_price,
            "reason": generate_match_explanation(
                item.track,
                requirements,
                calculate_match_score(item.track, requirements),
            ),
            "pre_clearance_status": "passes",
        }
        for item in ranked[:top_k]
    ]
    return {
        "scene_analysis": requirements.model_dump(),
        "recommendations": recommendations,
        "rejected_candidates": rejected,
        "total_candidates": len(candidates),
        "disclaimer": DISCLAIMER,
    }


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

    if os.getenv("SYNCAGENT_API_MODE", "fast").lower() == "fast":
        # The API fast path uses one Gemini call for scene understanding and
        # keeps catalog decisions entirely deterministic. The full ADK path
        # remains available with SYNCAGENT_API_MODE=adk.
        requirements = analyze_scene(scene_description)
        return AnalyzeResponse.model_validate({
            "success": True,
            **build_catalog_result(
                scene_analysis=requirements.model_dump(),
                budget=budget,
                territory=territory,
                top_k=top_k,
            ),
        }).model_dump()

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

            raise ValueError(
                f"SyncAgent returned invalid JSON: {e}"
            ) from e

        logger.info(
            "[%s] SyncAgent workflow completed",
            workflow_id
        )

        # The agent interprets the scene, while this deterministic pass owns
        # catalog truth, licensing decisions, and ranking output.
        catalog_result = build_catalog_result(
            scene_analysis=parsed.get("scene_analysis", {}),
            budget=budget,
            territory=territory,
            top_k=top_k,
        )
        validated = AnalyzeResponse.model_validate({
            "success": True,
            **catalog_result,
        })

        return validated.model_dump()

    except Exception:

        logger.exception(
            "[%s] SyncAgent workflow failed",
            workflow_id
        )

        raise
