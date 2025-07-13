from __future__ import annotations

import argparse
import os
import sqlite3
import subprocess
import sys
import json
import shutil
from pathlib import Path

# ─────────────── Configuration ───────────────
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SCHEMA_FILE = ROOT / "database" / "schema.sql"
DB_FILE = ROOT / "rpg-shopkeeper.db"
SETUP_PKG = "setup.setup_all"

ENTRYPOINTS = {
    "whatsapp": ROOT / "runapp" / "run_whatsapp_safe.py",
    "sms":      ROOT / "runapp" / "run_sms.py",
    "cli":      ROOT / "runapp" / "cli_safe.py",
}
PERSONALITIES_DIR = ROOT / "app" / "agents" / "personalities"
# ─────────────────────────────────────────────

def _touch_init(path: Path) -> None:
    (path / "__init__.py").touch(exist_ok=True)

def _ensure_packages() -> None:
    agents_pkg = ROOT / "app" / "agents"
    _touch_init(agents_pkg)
    if PERSONALITIES_DIR.exists():
        _touch_init(PERSONALITIES_DIR)
        for p in PERSONALITIES_DIR.iterdir():
            if p.is_dir():
                _touch_init(p)

def _collect_personality_modules() -> list[str]:
    mods: list[str] = []
    if PERSONALITIES_DIR.exists():
        for py in PERSONALITIES_DIR.rglob("*.py"):
            if py.name != "__init__.py":
                mods.append(".".join(py.relative_to(ROOT).with_suffix("").parts))
    return mods

def _validate_items(db_path: Path) -> None:
    try:
        with sqlite3.connect(db_path) as conn:
            n_items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    except sqlite3.Error as exc:
        sys.exit(f"❌ SQLite error while validating DB: {exc}")

    if n_items == 0:
        sys.exit("❌ 0 SRD items were imported – aborting build")

def _ensure_database(skip_srd: bool) -> None:
    if DB_FILE.exists():
        _validate_items(DB_FILE)
        return

    print("⚙️  Seeding database via setup/setup_all.py …")

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"

    args: list[str] = [sys.executable, "-m", SETUP_PKG, "--reset"]
    if skip_srd:
        args.append("--no-srd")

    subprocess.run(args, cwd=str(ROOT), env=env, check=True)

    if not DB_FILE.exists():
        sys.exit("❌ setup_all.py did not create rpg-shopkeeper.db")

    _validate_items(DB_FILE)

def build_target(mode, skip_srd, env):
    entry = ENTRYPOINTS[mode]
    if not entry.exists():
        sys.exit(f"‼ Entry script not found: {entry}")

    sep = ";" if os.name == "nt" else ":"

    _ensure_packages()
    _ensure_database(skip_srd=skip_srd)

    exe_name = f"rpg-shopkeeper-{mode}"
    DIST_DIR = Path(__file__).resolve().parent / "dist"
    exe_path = DIST_DIR / f"{exe_name}.exe"

    # Clean up previous build
    try:
        exe_path.unlink(missing_ok=True)
    except PermissionError:
        sys.exit(
            f"❌ {exe_path.name} is in use (or previewed in Explorer). "
            "Close it and run the build again."
        )

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile", "--clean", "--noconfirm",
        "--name", exe_name,
        "--hidden-import", "win32timezone",
    ]

    if (icon := ASSETS / "shop.ico").exists():
        cmd += ["--icon", str(icon)]

    # Bundle static assets
    if ASSETS.exists():
        cmd += ["--add-data", f"{ASSETS}{sep}assets"]
    if SCHEMA_FILE.exists():
        cmd += ["--add-data", f"{SCHEMA_FILE}{sep}database"]
    if DB_FILE.exists():
        cmd += ["--add-data", f"{DB_FILE}{sep}."]
    if (conf := ROOT / ".env").exists():
        cmd += ["--add-data", f"{conf}{sep}."]

    for mod in _collect_personality_modules():
        cmd += ["--hidden-import", mod]

    cmd.append(str(entry))

    print(f"🛠 Building [{mode}] ...\n  Running:", " ".join(map(str, cmd)))
    subprocess.run(cmd, env=env, check=True)

    # Copy dependencies to dist folder
    DEPENDENCY_FILES = [
        ROOT / ".env",
        ROOT / "ngrok.exe",
        # Add more dependencies here if needed
    ]
    for dep in DEPENDENCY_FILES:
        if dep.exists():
            shutil.copy(dep, DIST_DIR / dep.name)
            print(f"✔ Copied {dep.name} to {DIST_DIR}")
        else:
            print(f"⚠ Dependency not found: {dep} (skipped)")

def main():
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"
    parser = argparse.ArgumentParser(description="Freeze rpg-shopkeeper")
    parser.add_argument(
        "mode",
        choices=list(ENTRYPOINTS),
        nargs="?",
        help="Target executable (default: ALL)",
    )
    parser.add_argument(
        "--no-srd",
        action="store_true",
        help="Skip SRD item import while building the database",
    )
    args = parser.parse_args()

    if args.mode:
        build_target(args.mode, args.no_srd, env)
    else:
        print("🔨 No mode specified – building ALL targets!")
        for mode in ENTRYPOINTS:
            build_target(mode, args.no_srd, env)

if __name__ == "__main__":
    main()
