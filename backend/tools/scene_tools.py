import json

from backend.services.scene_analyzer import analyze_scene


def analyze_scene_tool(
    scene_description: str
) -> dict:
    """
    Analyze a film scene and convert it into structured
    music requirements.

    Use this tool whenever the user provides a film scene,
    screenplay excerpt, or scene description and music needs
    to be recommended.

    Args:
        scene_description: Detailed description of the film scene.

    Returns:
        Structured music requirements including mood, energy,
        BPM range, genres, instrumentation, pacing, and
        estimated scene duration.
    """

    requirements = analyze_scene(
        scene_description
    )

    return requirements.model_dump()