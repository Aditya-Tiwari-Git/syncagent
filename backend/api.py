import os
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.services.report_service import generate_clearance_report

from backend.models.api import (
    AnalyzeRequest,
    AnalyzeResponse,
)

from backend.services.agent_service import (
    run_syncagent,
)

from backend.services.logger import logger


# ---------------------------------------------------------
# Google Cloud / Vertex AI configuration
# ---------------------------------------------------------

if os.getenv("GOOGLE_CLOUD_PROJECT"):

    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

    os.environ.pop(
        "GOOGLE_API_KEY",
        None,
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
    version="0.1.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/")
async def root():

    return {
        "name": "SyncAgent",
        "status": "online",
    }


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
async def health():

    return {
        "status": "healthy",
    }


# ---------------------------------------------------------
# Helper: run and normalize SyncAgent response
# ---------------------------------------------------------

async def run_analysis(
    request: AnalyzeRequest,
    request_id: str | None = None,
):
    """
    Run SyncAgent and normalize its response into the
    same structure used by AnalyzeResponse.

    This prevents /api/analyze and /api/report from
    handling agent output differently.
    """

    result = await run_syncagent(
        scene_description=request.scene_description,
        budget=request.budget,
        territory=request.territory,
        top_k=request.top_k,
    )

    if not isinstance(result, dict):

        raise ValueError(
            "SyncAgent returned an invalid response type."
        )

    response = {
        "success": True,

        "scene_analysis": result.get(
            "scene_analysis",
            {},
        ),

        "recommendations": result.get(
            "recommendations",
            [],
        ),

        "rejected_candidates": result.get(
            "rejected_candidates",
            [],
        ),

        "total_candidates": result.get(
            "total_candidates",
            0,
        ),

        "disclaimer": result.get(
            "disclaimer",
            (
                "Final licensing must be verified "
                "with the relevant rights holder."
            ),
        ),
    }

    # Validate/normalize against your Pydantic model.
    validated = AnalyzeResponse.model_validate(
        response
    )

    return validated.model_dump()


# ---------------------------------------------------------
# Analyze scene
# ---------------------------------------------------------

@app.post(
    "/api/analyze",
    response_model=AnalyzeResponse,
)
async def analyze(
    request: AnalyzeRequest,
):

    request_id = str(
        uuid.uuid4()
    )

    logger.info(
        "[%s] Starting analysis",
        request_id,
    )

    try:

        logger.info(
            "[%s] Scene received | budget=%s | territory=%s | top_k=%s",
            request_id,
            request.budget,
            request.territory,
            request.top_k,
        )

        response = await run_analysis(
            request=request,
            request_id=request_id,
        )

        logger.info(
            "[%s] Analysis completed | recommendations=%s | rejected=%s",
            request_id,
            len(response["recommendations"]),
            len(response["rejected_candidates"]),
        )

        return response

    except Exception as e:

        logger.exception(
            "[%s] SyncAgent analysis failed",
            request_id,
        )

        raise HTTPException(
            status_code=500,
            detail={
                "request_id": request_id,
                "error": "Analysis failed. Check the server logs using the request ID.",
            },
        ) from e


# ---------------------------------------------------------
# Generate PDF report
# ---------------------------------------------------------

@app.post(
    "/api/report",
)
async def generate_report(
    request: AnalyzeRequest,
):

    request_id = str(
        uuid.uuid4()
    )

    logger.info(
        "[%s] Starting PDF report generation",
        request_id,
    )

    try:

        # IMPORTANT:
        # Use the same normalized analysis pipeline
        # as /api/analyze.
        result = await run_analysis(
            request=request,
            request_id=request_id,
        )

        logger.info(
            "[%s] Analysis ready for PDF | recommendations=%s | rejected=%s",
            request_id,
            len(result["recommendations"]),
            len(result["rejected_candidates"]),
        )

        pdf_buffer = generate_clearance_report(
            scene_description=request.scene_description,

            budget=request.budget,

            territory=request.territory,

            scene_analysis=result.get(
                "scene_analysis",
                {},
            ),

            recommendations=result.get(
                "recommendations",
                [],
            ),

            rejected_candidates=result.get(
                "rejected_candidates",
                [],
            ),
        )

        logger.info(
            "[%s] PDF report generated successfully",
            request_id,
        )

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    "attachment; "
                    'filename="syncagent-pre-clearance-report.pdf"'
                ),

                # Useful for debugging the request.
                "X-Request-ID": request_id,
            },
        )

    except Exception as e:

        logger.exception(
            "[%s] PDF report generation failed",
            request_id,
        )

        raise HTTPException(
            status_code=500,
            detail={
                "request_id": request_id,
                "error": "Report generation failed. Check the server logs using the request ID.",
            },
        ) from e
