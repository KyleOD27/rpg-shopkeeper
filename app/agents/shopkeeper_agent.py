# app/shopkeeper_agent.py — Final State-Aware Version

import os
import json
import random
import importlib
from openai import OpenAI
from dotenv import load_dotenv

from app.models.items import get_all_items
from app.agent_rules import BASE_AGENT_RULES
# config import DEBUG_MODE
DEBUG_MODE = False

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ACTIVE_AGENT = None


def shopkeeper_greeting(party_name: str, visit_count: int, player_name: str) -> str:
    if visit_count == 1:
        return f"Ah, {party_name} — first time in this shop? Nice to meet you, {player_name}."
    elif visit_count < 5:
        return f"{party_name} again? I think you might like it here, {player_name}."
    else:
        return f"Back already, {player_name}? I'm flattered. This is visit number {visit_count}!"

def shopkeeper_intro_prompt(self) -> str:
    return (
        "Welcome to the rpg store. My standard actions are  BUY, SELL, HAGGLE, DEPOSIT, WITHDRAW, CHECK_BALANCE, VIEW_lEDGER."
    )

def shopkeeper_fallback_prompt(self) -> str:
    item_names = [item["item_name"] for item in get_all_items()]
    return f"I’m not sure what you’re after, so here’s what we’ve got: {', '.join(item_names)}"

def shopkeeper_confirmation_reply(item_name, item_cost, new_balance):
    return (
        f"Very well. The '{item_name}' is yours for {item_cost} gold. "
        f"You now have {new_balance} gold remaining."
    )

def shopkeeper_clarify_item_prompt(self) -> str:
    item_names = [item["item_name"] for item in get_all_items()]
    return (
        f"I am aware you are looking for an item, but not sure which one. Here is what we have:{', '.join(item_names)}"
    )

def shopkeeper_buy_confirm_prompt(self, item, player_gold) -> str:
     return (
        f"Your current party balance is {player_gold} gold."
        f"You want to BUY item: {item['item_name']} for {item['base_price']} gold?"
        f"Give me a yes and we'll get it done."
    )


def shopkeeper_buy_success_prompt(self, item, result_message) -> str:
    return (
        f"You have just purchased a {item['item_name']} for {item['base_price']} gold. Congratulations!" 
        f"I'll add it to the list."
    )

def shopkeeper_buy_failure_prompt(self, item, result_message, player_gold) -> str:
    return (
            f"I am sorry you can not afford to buy a {item['item_name']} for {item['base_price']} gold."
            f"Your balance is only: {player_gold}"
    )

def shopkeeper_buy_cancel_prompt(self, item) -> str:
        return (
            f"So you don't want {item['item_name']}?"
    )


##break

def set_active_agent(agent_name):
    global ACTIVE_AGENT
    agent_module = importlib.import_module(f'app.agents.personalities.{agent_name.lower()}')
    agent_class = getattr(agent_module, agent_name)
    ACTIVE_AGENT = agent_class()



def build_system_prompt():
    if not ACTIVE_AGENT:
        raise ValueError("ACTIVE_AGENT not set. Please call set_active_agent() first.")

    items = get_all_items()
    item_names = [item['item_name'] for item in items]

    standard_actions = [
        "buy", "sell", "haggle", "deposit", "withdraw", "check_balance", "ledger"
    ]

    return (
        ACTIVE_AGENT.system_prompt
        + "\n\n"
        + BASE_AGENT_RULES
        + "\n\nStandard Actions the player can take: "
        + ", ".join(standard_actions)
        + "\n\nYour shop sells: " + ", ".join(item_names)
        + "\n\nIMPORTANT FINAL RULE:\nYou will ONLY respond as the shopkeeper.\nYou will NEVER generate what the player says or does.\nIf the player is trying to buy but the item is unclear or missing, DO NOT guess. Ask them clearly which item they want and optionally suggest a few items you sell.\nRespond to the player's message only."
    )


def build_contextual_prompt(player_input, state=None, intent=None, action=None, item=None):
    base = build_system_prompt()

    context_lines = ["CURRENT GAME CONTEXT:"]

    if hasattr(state, 'awaiting_input') and state.awaiting_input == 'item_name':
        context_lines.append("You are awaiting the player to name the item they want to buy. Do NOT assume the item. Ask them to clarify.")

    if state:
        context_lines.append(f"Current Conversation State: {getattr(state, 'name', 'N/A')}")
    if intent:
        context_lines.append(f"Detected Player Intent: {getattr(intent, 'name', 'N/A')}")
    if action:
        context_lines.append(f"Pending Action: {action}")
    if item:
        context_lines.append(f"Pending Item: {item}")

    context_lines.append("Behavior Rules:")
    context_lines.append("If in state AWAITING_ITEM_SELECTION, always ask the player what item they want to buy and offer a few suggestions from your shop.")
    context_lines.append("If in state AWAITING_CONFIRMATION, confirm the specific item and price before completing the transaction.")

    context_lines.append("Respond as the shopkeeper ONLY in this context.")
    context_lines.append(f"Player says: {player_input}")

    full_prompt = base + "\n\n" + "\n".join(context_lines)

    if DEBUG_MODE:
        print("\n=== DEBUG: CONTEXTUAL PROMPT START ===")
        print(full_prompt)
        print("=== DEBUG: CONTEXTUAL PROMPT END ===\n")

    return full_prompt


def generate_agent_reply(player_input, state=None, intent=None, action=None, item=None):
    if not ACTIVE_AGENT:
        raise ValueError("ACTIVE_AGENT not set. Please call set_active_agent() first.")

    if player_input in ["fallback_action_prompt", "ask_item_buy"]:
        return generate_fallback_reply(player_input)

    prompt = build_contextual_prompt(player_input, state, intent, action, item)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )
    except Exception as e:
        print("GPT API Error:", e)
        return {"type": "text", "data": "The shopkeeper scowls silently. Try again."}

    reply = response.choices[0].message.content.strip()
    return {"type": "text", "data": reply}


def generate_fallback_reply(category):
    fallback_lines = {
        "action_prompt": [
            "Spit it out. Here's what I actually do around here:",
            "Words. Use them. What do you want?",
            "This is a shop, not a confessional. Pick something:",
        ],
        "ask_item_buy": [
            f"What exactly do you want to buy? Try something like: {', '.join([i['item_name'] for i in get_all_items()[:3]])}",
            "I'm not a mind reader. Try naming the item next time.",
            "Buying what, exactly? Use your words. I sell more than dreams.",
        ]
    }
    line = random.choice(fallback_lines.get(category, ["..."]))
    return {"type": "text", "data": line}


def chat_with_gpt(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns structured JSON responses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("GPT Interpreter Error:", e)
        return '{"intent": "UNKNOWN", "item": null}'

from app.conversation import PlayerIntent

def check_confirmation_via_gpt(user_input: str):
    system_prompt = (
        "You are a classifier that determines whether a user's sentence is a CONFIRMATION, "
        "a CANCELLATION, or UNKNOWN. "
        "Return JSON in this format: { \"intent\": \"CONFIRM\" | \"CANCEL\" | \"UNKNOWN\", \"confidence\": <int 0–100> }."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"\"{user_input}\""}
            ],
            temperature=0.0,
            max_tokens=100,
        )

        result = json.loads(response.choices[0].message.content.strip())

        if DEBUG_MODE:
            print(f"[DEBUG] GPT confirmation classifier: {result}")

        if result.get("confidence", 0) >= 85:
            if result["intent"] == "CONFIRM":
                return PlayerIntent.CONFIRM
            elif result["intent"] == "CANCEL":
                return PlayerIntent.CANCEL

    except Exception as e:
        print("[GPT CONFIRM CHECK ERROR]", e)

    return PlayerIntent.UNKNOWN

