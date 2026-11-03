"""Stop hook: don't let the agent say "done" while the tests it may have broken are red.

Runs only when there is something to verify:
- in a git repo: only if there are uncommitted changes to project files (outside .forja/);
- outside git: always (evals make the work copy a git repo, so read-only tasks are not affected).
Then runs pytest; if it fails, exit 2 sends the failure tail back to the model so it keeps working.
The harness gives the agent at most 3 extra rounds, so this can never loop forever.
"""
import json
import subprocess
import sys

json.load(sys.stdin)  # {"hook_event_name": "Stop", "cwd": ..., "last_assistant_message": ...}


def changed_files() -> list[str] | None:
    """Changed paths relative to cwd, or None if this is not a git repo."""
    try:
        p = subprocess.run(["git", "status", "--porcelain", "--", "."], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if p.returncode != 0:
        return None
    paths = [line[3:].strip() for line in p.stdout.splitlines() if line.strip()]
    return [x for x in paths if ".forja/" not in x and "__pycache__" not in x]


changed = changed_files()
if changed is not None and not changed:
    sys.exit(0)  # nothing changed: a plain question, nothing to verify

try:
    t = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "--no-header", "-p", "no:cacheprovider"],
                       capture_output=True, text=True, timeout=300)
except subprocess.TimeoutExpired:
    print("The test suite timed out (300 s). Check for infinite loops before finishing.", file=sys.stderr)
    sys.exit(2)

if t.returncode in (0, 5):  # 5 = no tests collected
    sys.exit(0)
tail = "\n".join((t.stdout + t.stderr).strip().splitlines()[-15:])
print("You are not done yet: the test suite fails after your changes. Fix it (do not edit the tests) and then answer.\n"
      + tail, file=sys.stderr)
sys.exit(2)
