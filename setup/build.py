# setup/build.py – revamped
# -----------------------------------------------------------------------------
# This version removes the fragile DB rename step, validates the seed, and
# bundles the SQLite file directly with the executable.  It also cleans up
# a couple of edge‑cases around package discovery.
# -----------------------------------------------------------------------------

from __future__ import annotations

import argparse
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

# ───────────────────────── Configuration ──────────────────────────
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SCHEMA_FILE = ROOT / "database" / "schema.sql"
DB_FILE = ROOT / "rpg-shopkeeper.db"  # single source‑of‑truth!
SETUP_PKG = "setup.setup_all"

ENTRYPOINTS = {
    "whatsapp": ROOT / "RunApp" / "run_whatsapp.py",
    "sms": ROOT / "RunApp" / "run_sms.py",
    "cli": ROOT / "RunApp" / "cli_safe.py",
}
PERSONALITIES_DIR = ROOT / "app" / "agents" / "personalities"
# ──────────────────────────────────────────────────────────────────


# ───────────────────────── helpers ────────────────────────────────

def _touch_init(path: Path) -> None:
    """Ensure a directory is a Python package."""
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
    """Return fully‑qualified import paths so PyInstaller bundles them."""
    mods: list[str] = []
    if PERSONALITIES_DIR.exists():
        for py in PERSONALITIES_DIR.rglob("*.py"):
            if py.name != "__init__.py":
                mods.append(".".join(py.relative_to(ROOT).with_suffix("").parts))
    return mods


# ───────────── database seeding / validation ─────────────────────

def _validate_items(db_path: Path) -> None:
    """Abort the build if the seed produced an empty items table."""
    try:
        with sqlite3.connect(db_path) as conn:
            n_items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    except sqlite3.Error as exc:  # pragma: no cover – sanity guard
        sys.exit(f"❌ SQLite error while validating DB: {exc}")

    if n_items == 0:
        sys.exit("❌ 0 SRD items were imported – aborting build")


def _ensure_database(skip_srd: bool) -> None:
    """Seed the DB the first time we build (or if the file was removed)."""

    if DB_FILE.exists():
        _validate_items(DB_FILE)
        return  # already seeded & validated

    print("⚙️  Seeding database via setup/setup_all.py …")

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}{os.pathsep}{env.get('PYTHONPATH', '')}"

    # Always pass --reset so we have a deterministic DB after each build
    args: list[str] = [sys.executable, "-m", SETUP_PKG, "--reset"]
    if skip_srd:
        args.append("--no-srd")

    subprocess.run(args, cwd=str(ROOT), env=env, check=True)

    if not DB_FILE.exists():
        sys.exit("❌ setup_all.py did not create rpg-shopkeeper.db")

    _validate_items(DB_FILE)


# ───────────────────────── main build ────────────────────────────

def main() -> None:  # noqa: C901 – a little long but self‑contained
    parser = argparse.ArgumentParser(description="Freeze rpg-shopkeeper")
    parser.add_argument(
        "mode",
        choices=ENTRYPOINTS,
        nargs="?",
        default="whatsapp",
        help="Target executable (default: whatsapp)",
    )
    parser.add_argument(
        "--no-srd",
        action="store_true",
        help="Skip SRD item import while building the database",
    )
    args = parser.parse_args()

    entry = ENTRYPOINTS[args.mode]
    if not entry.exists():
        sys.exit(f"‼ Entry script not found: {entry}")

    _ensure_packages()
    _ensure_database(skip_srd=args.no_srd)

    sep = ";" if sys.platform == "win32" else ":"
    exe_path = ROOT / "dist" / f"rpg-shopkeeper-{args.mode}.exe"
    exe_path.unlink(missing_ok=True)

    cmd: list[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--name",
        f"rpg-shopkeeper-{args.mode}",
    ]

    if args.mode != "cli":
        cmd.append("--noconsole")

    if (icon := ASSETS / "shop.ico").exists():
        cmd += ["--icon", str(icon)]

    if ASSETS.exists():
        cmd += ["--add-data", f"{ASSETS}{sep}assets"]
    if SCHEMA_FILE.exists():
        cmd += ["--add-data", f"{SCHEMA_FILE}{sep}database"]
    if DB_FILE.exists():
        # Bundle the live DB right next to the executable inside the bundle
        cmd += ["--add-data", f"{DB_FILE}{sep}."]

    # ––– inside build.py, right after the other --add-data lines –––
    conf = ROOT / ".env"
    if conf.exists():
        cmd += ["--add-data", f"{conf}{sep}."]  # drops .env next to EXE

    for mod in _collect_personality_modules():
        cmd += ["--hidden-import", mod]

    cmd.append(str(entry))

    print("🛠 Running:", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
