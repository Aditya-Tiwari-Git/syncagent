MOOD_NORMALIZATION = {
    "sad": "melancholic",
    "lonely": "melancholic",
    "depressed": "melancholic",

    "scary": "dark",
    "mysterious": "dark",

    "exciting": "energetic",
    "powerful": "energetic",

    "calm": "peaceful",
    "relaxing": "peaceful",
}


def normalize_mood(mood: str) -> str:

    mood = mood.lower().strip()

    return MOOD_NORMALIZATION.get(
        mood,
        mood
    )