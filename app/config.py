# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class RuntimeFlags:
    DEBUG_MODE = False

TRACE_MODE = False

# Shop Settings
SHOP_NAME = "RPG Shop"

# Optional login override
AUTO_LOGIN_NAME = "Kyle"       # or None
AUTO_LOGIN_PIN = "1234"     # or None

#TWILIO RECOVERY CODE: KRY122T9YNPNGP9L7D83Y6MN