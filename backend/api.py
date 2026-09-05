import json
import os
import uuid

from fastapi import FastAPI, HTTPException

from backend.models.api import (
    AnalyzeRequest,
    AnalyzeResponse
)

from backend.services.agent_service import (
    run_syncagent
)

from backend.services.logger import logger


# ---------------------------------------------------------
# Google Cloud / Vertex AI configuration
# ---------------------------------------------------------

# Prefer Vertex AI when a Google Cloud project is configured.
if os.getenv("GOOGLE_CLOUD_PROJECT"):

    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

    # Prevent accidental use of GOOGLE_API_KEY
    # when Vertex AI is being used.
    os.environ.pop(
        "GOOGLE_API_KEY",
        None
    )


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="SyncAgent API",
    description=(
        "AI-powered music pre-clearance "
        "agent for filmmakers"
    ),
    version="0.1.0"
)


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/")
async def root():

    return {
        "name": "SyncAgent",
        "status": "online"
    }


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# Analyze scene
# ---------------------------------------------------------

@app.post(
    "/api/analyze",
    response_model=AnalyzeResponse
)
async def analyze(
    request: AnalyzeRequest
):

    request_id = str(
        uuid.uuid4()
    )

    logger.info(
        "[%s] Starting analysis",
        request_id
    )

    try:

        logger.info(
            "[%s] Scene received | budget=%s | territory=%s | top_k=%s",
            request_id,
            request.budget,
            request.territory,
            request.top_k
        )

        result = await run_syncagent(
            scene_description=(
                request.scene_description
            ),

            budget=request.budget,

            territory=request.territory,

            top_k=request.top_k
        )

        logger.info(
            "[%s] Agent workflow returned successfully",
            request_id
        )

        print("\n===== AGENT RESULT =====")
        print(
            json.dumps(
                result,
                indent=2
            )
        )
        print("========================\n")

        response = {
            "success": True,

            "scene_analysis": result.get(
                "scene_analysis",
                {}
            ),

            "recommendations": result.get(
                "recommendations",
                []
            ),

            "rejected_candidates": result.get(
                "rejected_candidates",
                []
            ),

            "total_candidates": result.get(
                "total_candidates",
                0
            ),

            "disclaimer": result.get(
                "disclaimer",
                (
                    "Final licensing must be verified "
                    "with the relevant rights holder."
                )
            )
        }

        logger.info(
            "[%s] Analysis completed | recommendations=%s | rejected=%s",
            request_id,
            len(response["recommendations"]),
            len(response["rejected_candidates"])
        )

        print(
            f"[{request_id}] Analysis completed"
        )

        return response

    except Exception as e:

        logger.exception(
            "[%s] SyncAgent analysis failed",
            request_id
        )

        print(
            f"[{request_id}] Analysis failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "request_id": request_id,
                "error": str(e)
            }
        ) from e
