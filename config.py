# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Flags
DEBUG_MODE = True
TRACE_MODE = False

# Shop Settings
#SHOP_NAME = "Grizzlebeard's Emporium"
SHOP_NAME = "RPG Shop"

# Enabled Shops
SHOP_NAMES = [
    "Grizzlebeard's Emporium",
    "Merlinda's Curios",
    "Skabfang's Shack",
    "RPG Shop"
]

# Player Settings
DEFAULT_PLAYER_NAME = "Thistle"
