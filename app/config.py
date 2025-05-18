# app/config.py
from __future__ import annotations
import os, sys
from pathlib import Path
from dotenv import load_dotenv

# ------------------------------------------------------------
# Where is the executable running from?
# ------------------------------------------------------------
if getattr(sys, "frozen", False):                # running under PyInstaller
    exe_dir = Path(sys.executable).parent        # …/dist/ or …/dist/app/
else:                                            # normal source run
    exe_dir = Path(__file__).resolve().parent

# ------------------------------------------------------------
# Load .env sitting **next to that executable/folder**
# ------------------------------------------------------------
env_file = exe_dir / ".env"
load_dotenv(env_file)

print(f"[CONFIG] .env looked for at {env_file}  –  exists? {env_file.exists()}")

# ------------------------------------------------------------
# Public settings
# ------------------------------------------------------------
SHOP_NAME  = os.getenv("SHOP_NAME", "RPG Shop")
DEBUG_MODE = os.getenv("DEBUG_MODE", "0") == "1"

class RuntimeFlags:
    DEBUG_MODE = DEBUG_MODE
