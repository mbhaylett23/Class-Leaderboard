#!/usr/bin/env python3
"""Utility launcher for the Streamlit classroom leaderboard."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import List

try:
    import psutil  # type: ignore
except ImportError as exc:  # pragma: no cover - defensive
    print("psutil is required for run_app.py. Install it via `conda install psutil`.")
    raise SystemExit(1) from exc

ROOT = Path(__file__).resolve().parent
ENV_NAME = "leaderboard_env"
APP_PATH = ROOT / "streamlit_app" / "app.py"
SECRETS_PATH = ROOT / "streamlit_app" / ".streamlit" / "secrets.toml"
LEADERBOARD_URL = "http://localhost:8501/?view=leaderboard"
MAIN_URL = "http://localhost:8501"


def print_status(message: str) -> None:
    """Prefix log lines for easy scanning."""
    print(f"[run_app] {message}")


def find_streamlit_processes() -> List[psutil.Process]:
    """Return running Streamlit processes (excluding this launcher)."""
    current_pid = os.getpid()
    matches: List[psutil.Process] = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        if proc.info.get("pid") == current_pid:
            continue
        try:
            cmdline = proc.info.get("cmdline") or []
            name = (proc.info.get("name") or "").lower()
            if "streamlit" in name or any("streamlit" in part for part in cmdline):
                matches.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return matches


def kill_existing_streamlit(timeout: float = 5.0) -> None:
    """Terminate stray Streamlit processes to avoid port conflicts."""
    procs = find_streamlit_processes()
    if not procs:
        print_status("No existing Streamlit processes found.")
        return
    for proc in procs:
        try:
            print_status(f"Stopping Streamlit process PID={proc.pid}.")
            proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    gone, alive = psutil.wait_procs(procs, timeout=timeout)
    for proc in alive:
        try:
            print_status(f"Force killing PID={proc.pid} after timeout.")
            proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    print_status(f"Stopped {len(procs)} existing Streamlit process(es).")


def check_environment() -> None:
    """Verify app entrypoint and secrets are present before launch."""
    if not APP_PATH.exists():
        raise SystemExit("streamlit_app/app.py not found. Run from the project root.")
    if not SECRETS_PATH.exists():
        raise SystemExit(
            "Missing streamlit_app/.streamlit/secrets.toml. Copy the template and add real secrets."
        )
    placeholders = ["@youruni.edu", "your-project-id", "your-web-api-key", "YOUR_KEY_ID"]
    try:
        secrets_text = SECRETS_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Unable to read secrets.toml: {exc}") from exc
    hits = [token for token in placeholders if token in secrets_text]
    if hits:
        print_status(
            "⚠️  secrets.toml still contains placeholder values: " + ", ".join(hits)
        )


def conda_env_exists(env_name: str) -> bool:
    """Return True if the requested conda environment is available."""
    try:
        result = subprocess.run(
            ["conda", "env", "list", "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print_status("Conda executable not found on PATH. Falling back to current interpreter.")
        return False
    except subprocess.CalledProcessError as exc:
        print_status(f"Failed to query conda environments: {exc}")
        return False
    try:
        envs = json.loads(result.stdout).get("envs", [])
    except json.JSONDecodeError:
        print_status("Unable to parse conda env list output; continuing without conda run.")
        return False
    return any(Path(path).name == env_name for path in envs)


def start_streamlit(use_conda: bool) -> int:
    """Launch Streamlit (optionally via conda run) and stream logs until exit."""
    if use_conda:
        cmd = ["conda", "run", "-n", ENV_NAME, "streamlit", "run", str(APP_PATH)]
        print_status(f"Starting Streamlit via conda environment '{ENV_NAME}'.")
    else:
        cmd = [sys.executable, "-m", "streamlit", "run", str(APP_PATH)]
        print_status("Starting Streamlit using the current Python interpreter.")
    env = os.environ.copy()
    root_path = str(ROOT)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = root_path if not existing else f"{root_path}{os.pathsep}{existing}"
    print_status(f"Main app URL: {MAIN_URL}")
    print_status(f"Leaderboard URL: {LEADERBOARD_URL}")
    process = subprocess.Popen(cmd, cwd=ROOT, env=env)
    print_status(f"Streamlit process started with PID={process.pid}.")
    try:
        return process.wait()
    except KeyboardInterrupt:
        print_status("Keyboard interrupt received; shutting down Streamlit.")
        try:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=5)
        except Exception:
            process.kill()
            process.wait()
        return 0


def main() -> None:
    """Entrypoint orchestrating environment checks and process management."""
    print_status("Checking environment...")
    check_environment()
    kill_existing_streamlit()
    env_available = conda_env_exists(ENV_NAME)
    if env_available:
        print_status("Conda environment detected. Using `conda run` to launch Streamlit.")
    else:
        print_status("Proceeding without conda run. Ensure dependencies are installed here.")
    exit_code = start_streamlit(env_available)
    if exit_code:
        raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
