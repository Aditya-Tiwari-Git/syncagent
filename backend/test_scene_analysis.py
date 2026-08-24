from backend.services.scene_analyzer import analyze_scene


scene = """
A detective walks alone through an empty Mumbai street
at 2 AM after failing to solve a murder case.

It is raining lightly.

He feels exhausted, isolated and hopeless.
"""


result = analyze_scene(scene)

print("\nSCENE REQUIREMENTS\n")

print(result.model_dump_json(
    indent=4
))