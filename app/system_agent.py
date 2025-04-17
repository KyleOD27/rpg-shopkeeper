# app/system_agent.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from config import DEBUG_MODE

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SHOP_NAMES = [
    "Grizzlebeard's Emporium",
    "Merlinda's Curios",
    "Skabfang's Shack",
    "RPG Shop"
]

SYSTEM_PROMPT = (
    "You are the system assistant for a Dungeons & Dragons shop game."
    "\n\nThe player wants to visit a shop."
    "\n\nMatch their input to one of these shop names exactly:"
    f"\n- {SHOP_NAMES[0]}"
    f"\n- {SHOP_NAMES[1]}"
    f"\n- {SHOP_NAMES[2]}"
    "\n\nRespond ONLY with this JSON format:"
    "\n{\n  \"shop_name\": \"<exact shop name>\"\n}"
)


def choose_shop_via_gpt(player_input):
    if DEBUG_MODE:
        print("\n=== DEBUG: SYSTEM SHOP SELECTION PROMPT START ===")
        print(SYSTEM_PROMPT)
        print("=== DEBUG: SYSTEM SHOP SELECTION PROMPT END ===\n")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"The player says: {player_input}"},
            ],
            temperature=0,
            max_tokens=100,
        )
    except Exception as e:
        print("GPT API Error:", e)
        return None

    reply = response.choices[0].message.content.strip()

    try:
        result = json.loads(reply)
        return result.get("shop_name")
    except json.JSONDecodeError:
        return None
