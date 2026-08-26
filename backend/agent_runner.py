import asyncio
import os
import time
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

# Prefer Vertex AI when a Google Cloud project is configured.
if os.getenv("GOOGLE_CLOUD_PROJECT"):
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
    os.environ.pop("GOOGLE_API_KEY", None)

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from backend.agents.root_agent import root_agent


APP_NAME = "syncagent"
USER_ID = "local-user"
SESSION_ID = "day6-test"


def log(message: str):
    """Print timestamped progress information."""
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}", flush=True)


def inspect_event(event):
    """
    Print useful information from an ADK event.
    This is intentionally defensive because Event fields
    can vary between ADK versions.
    """

    print("\n" + "=" * 80)

    # Basic event information
    print("EVENT")
    print("=" * 80)

    print("Author:", getattr(event, "author", None))
    print("Invocation ID:", getattr(event, "invocation_id", None))
    print("Event ID:", getattr(event, "id", None))

    # Final response?
    try:
        print("Final response:", event.is_final_response())
    except Exception:
        pass

    # Content
    content = getattr(event, "content", None)

    if content:
        print("\nCONTENT:")

        parts = getattr(content, "parts", None)

        if parts:
            for i, part in enumerate(parts):
                print(f"\n  Part {i}:")

                text = getattr(part, "text", None)

                if text:
                    print("    TEXT:")
                    print("    " + text.replace("\n", "\n    "))

                function_call = getattr(part, "function_call", None)

                if function_call:
                    print("    FUNCTION CALL:")
                    print("      Name:", getattr(
                        function_call,
                        "name",
                        None
                    ))

                    print("      Args:", getattr(
                        function_call,
                        "args",
                        None
                    ))

                function_response = getattr(
                    part,
                    "function_response",
                    None
                )

                if function_response:
                    print("    FUNCTION RESPONSE:")
                    print("      Name:", getattr(
                        function_response,
                        "name",
                        None
                    ))

                    print("      Response:", getattr(
                        function_response,
                        "response",
                        None
                    ))

    # Actions
    actions = getattr(event, "actions", None)

    if actions:
        print("\nACTIONS:")
        print(actions)

    # Error
    error_code = getattr(event, "error_code", None)
    error_message = getattr(event, "error_message", None)

    if error_code or error_message:
        print("\nERROR:")
        print("  Code:", error_code)
        print("  Message:", error_message)

    print("=" * 80)


async def run_agent():

    start_time = time.perf_counter()

    log("SYNCAGENT STARTING")

    # ------------------------------------------------------------------
    # SESSION
    # ------------------------------------------------------------------

    log("Creating session service...")

    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    log("Session created")

    # ------------------------------------------------------------------
    # RUNNER
    # ------------------------------------------------------------------

    log("Creating ADK Runner...")

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    log("Runner created")

    # ------------------------------------------------------------------
    # USER MESSAGE
    # ------------------------------------------------------------------

    user_message = """
I need music for this scene:

Sad nighttime scene
Budget: $50
Territory: worldwide

Find suitable music, reject candidates that fail
pre-clearance checks, and explain your final recommendations.
"""

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=user_message
            )
        ],
    )

    log("User message prepared")

    # ------------------------------------------------------------------
    # RUN AGENT
    # ------------------------------------------------------------------

    log("Starting agent...")
    log("Waiting for ADK / Gemini / MCP...")

    event_number = 0

    try:

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=message,
        ):

            event_number += 1

            elapsed = time.perf_counter() - start_time

            print(
                f"\n\n"
                f"EVENT #{event_number} "
                f"(+{elapsed:.2f}s)"
            )

            inspect_event(event)

            # ----------------------------------------------------------
            # FINAL RESPONSE
            # ----------------------------------------------------------

            if (
                event.is_final_response()
                and event.content
            ):

                print("\n")
                print("#" * 80)
                print("SYNCAGENT FINAL RESPONSE")
                print("#" * 80)

                for part in event.content.parts:

                    if part.text:
                        print(part.text)

                print("#" * 80)

    except Exception as e:

        elapsed = time.perf_counter() - start_time

        print("\n")
        print("!" * 80)
        print("SYNCAGENT ERROR")
        print("!" * 80)

        print("Elapsed:", f"{elapsed:.2f}s")
        print("Exception type:", type(e).__name__)
        print("Exception:", e)

        import traceback

        traceback.print_exc()

        print("!" * 80)

        raise

    finally:

        total_time = time.perf_counter() - start_time

        print("\n")
        print("=" * 80)
        print("SYNCAGENT FINISHED")
        print("=" * 80)

        print("Events:", event_number)
        print("Total time:", f"{total_time:.2f}s")
        print("=" * 80)


if __name__ == "__main__":

    asyncio.run(
        run_agent()
    )
