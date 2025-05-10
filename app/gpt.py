import os
from openai import OpenAI
from dotenv import load_dotenv
from app.models.items import get_all_items
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def grizzlebeard_reply(player_input, context_note=''):
    items = get_all_items()
    item_names = [item['item_name'] for item in items]
    system_prompt = f"""
You are Grizzlebeard, a grumpy old dwarven shopkeeper in a Dungeons & Dragons world.

Your style is sarcastic, blunt, and occasionally kind — but only for profit.

Never break character.

Shop Inventory:
{', '.join(item_names)}

Only offer items that exist in the shop.

If the player asks for something you don't stock, suggest the closest item or mock them.

Optional Note for Context:
{context_note}
"""
    response = client.chat.completions.create(model='gpt-3.5-turbo',
        messages=[{'role': 'system', 'content': system_prompt}, {'role':
        'user', 'content': player_input}], temperature=0.7, max_tokens=150)
    reply = response.choices[0].message.content.strip()
    return reply
