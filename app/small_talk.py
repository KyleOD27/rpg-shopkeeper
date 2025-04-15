# app/small_talk.py

SMALL_TALK_KEYWORDS = [
    "thank", "thanks", "cheers",
    "hello", "hi", "greetings",
    "goodbye", "bye", "see ya", "farewell",
    "sup", "yo", "how's it going", "how are you"
]


def is_small_talk(player_input: str) -> bool:
    """
    Check if the player input is casual small talk.
    """
    lowered = player_input.lower()
    return any(keyword in lowered for keyword in SMALL_TALK_KEYWORDS)
