import json, os, pathlib, subprocess, sys

ENV = "leaderboard_env"
REQ = pathlib.Path(__file__).with_name("requirements.txt")
run = lambda cmd: subprocess.run(cmd, capture_output=True, text=True)
info = run(["conda", "env", "list", "--json"])
if info.returncode:
    print("❌ Unable to query conda environments."); sys.exit(3)
paths = json.loads(info.stdout).get("envs", [])
if not any(p.endswith(os.sep + ENV) or p.split(os.sep)[-1] == ENV for p in paths):
    print(f"❌ Conda env '{ENV}' not found."); sys.exit(1)
if not REQ.exists():
    print("❌ Missing requirements.txt."); sys.exit(3)
reqs = [r for r in REQ.read_text().splitlines() if r and not r.startswith("#")]
missing = [r for r in reqs if run(["conda", "run", "-n", ENV, "python", "-c", f"import pkg_resources; pkg_resources.require({r!r})"]).returncode]
if missing:
    print("❌ Packages missing or mismatched:", ", ".join(missing))
    print("Run: conda run -n leaderboard_env pip install -r requirements.txt")
    sys.exit(2)
print("✅ Environment ready. Run setup_step2_firebase.py")
