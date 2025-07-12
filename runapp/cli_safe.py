# runapp/cli_safe.py   ← new tiny wrapper (or paste at bottom of cli.py)
import datetime, csv, traceback, sys
from pathlib import Path

# ---- import your real entry point -------------------------------------
from runapp.cli import main   # adjust the import if main() lives elsewhere
# ----------------------------------------------------------------------

LOG_PATH = Path(__file__).resolve().parent / "error_log.csv"

def run():
    try:
        main()                     # <-- your normal CLI
    except Exception as exc:        # catch *everything*
        tb = traceback.format_exc()
        ts = datetime.datetime.now().isoformat(timespec="seconds")

        # 1) print for the user
        print("\n================= CRASH =================")
        print(tb)

        # 2) save to CSV  (create header once)
        new_file = not LOG_PATH.exists()
        with LOG_PATH.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow(["timestamp", "exc_type", "message", "traceback"])
            writer.writerow([ts, type(exc).__name__, str(exc), tb])

        # 3) keep window open
        input("\nPress <Enter> to close this window…")
        sys.exit(1)                 # non-zero = failure for CI etc.

if __name__ == "__main__":
    run()
