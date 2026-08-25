MOOD_MAP = {

    "sad": "melancholic",
    "lonely": "melancholic",
    "heartbroken": "melancholic",
    "depressed": "melancholic",

    "scary": "dark",
    "mysterious": "dark",
    "ominous": "dark",

    "joyful": "happy",
    "cheerful": "happy",

    "uplifting": "hopeful",
    "optimistic": "hopeful",

    "exciting": "energetic",
    "intense": "tense"
}


def normalize_mood(
    mood: str
) -> str:

    mood = mood.lower().strip()

    return MOOD_MAP.get(
        mood,
        mood
    )


def normalize_moods(
    moods: list[str]
) -> list[str]:

    normalized = []

    for mood in moods:

        normalized.append(
            normalize_mood(mood)
        )

    return list(
        set(normalized)
    )