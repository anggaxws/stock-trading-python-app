import os
import sys
import time
import schedule
import subprocess
from datetime import datetime


def basic_job():
    print("[basic_job] Job started at:", datetime.now().isoformat())


def run_stock_job():
    print("[run_stock_job] Starting stock job at:", datetime.now().isoformat())

    base_dir = os.path.abspath(os.path.dirname(__file__))
    candidate_paths = [
        os.path.join(base_dir, "script.py"),
        os.path.join(base_dir, "stock-trading-python-app", "script.py"),
        os.path.join(base_dir, "..", "stock-trading-python-app", "script.py"),
    ]

    script_path = None
    for p in candidate_paths:
        p = os.path.abspath(p)
        if os.path.isfile(p):
            script_path = p
            break

    if script_path is None:
        print("[run_stock_job] ERROR: script not found in any candidate path:")
        for p in candidate_paths:
            print("  -", os.path.abspath(p))
        return

    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(script_path),
        timeout=300,
    )

    if result.stdout:
        print("[run_stock_job] stdout:\n", result.stdout.strip())

    if result.stderr:
        print("[run_stock_job] stderr:\n", result.stderr.strip())

    if result.returncode != 0:
        print(f"[run_stock_job] FAILED (exit code {result.returncode})")
    else:
        print(f"[run_stock_job] Completed successfully at {datetime.now().isoformat()}")


if __name__ == "__main__":
    # example schedule from screenshot style
    schedule.every().minute.do(basic_job)
    schedule.every().minute.do(run_stock_job)

    print("Scheduler started. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("Scheduler stopped by user.")
