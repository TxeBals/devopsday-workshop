"""PreToolUse (bash): blocks commands that read or export secrets. Exit 2 = block; stderr goes to the model."""
import json
import re
import sys

event = json.load(sys.stdin)
cmd = event.get("tool_input", {}).get("command", "")
if re.search(r"(\.env\b|id_rsa|\.aws/credentials|printenv|\benv\b\s*$|AWS_SECRET|API_KEY)", cmd):
    print(f"Command blocked by policy: it may expose secrets ({cmd!r}).", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
