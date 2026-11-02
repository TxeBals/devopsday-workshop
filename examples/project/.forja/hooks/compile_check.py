"""PostToolUse (edit_file|write_file): if the edited Python file doesn't compile, return the error to the model (exit 2)."""
import json
import py_compile
import sys

event = json.load(sys.stdin)
path = event.get("tool_input", {}).get("path", "")
if path.endswith(".py"):
    try:
        py_compile.compile(path, doraise=True)
    except py_compile.PyCompileError as e:
        print(f"The edited file doesn't compile:\n{e.msg}", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
