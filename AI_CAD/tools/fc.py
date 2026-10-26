#!/usr/bin/env python
"""FreeCAD XML-RPC bridge client.

Usage:
  python fc.py "import FreeCAD; _result_ = FreeCAD.Version()"
  python fc.py --file script.py

Code runs inside the live FreeCAD process. Set `_result_` (JSON-serializable)
to get a return value. Stdout of the executed code is returned under
`stdout`.
"""
import sys
import json
import xmlrpc.client

HOST = "localhost"
PORT = 9875

def run(code: str):
    proxy = xmlrpc.client.ServerProxy(f"http://{HOST}:{PORT}", allow_none=True)
    res = proxy.execute(code)
    return res if isinstance(res, dict) else {"result": res}

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--file":
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            code = f.read()
    else:
        code = sys.argv[1] if len(sys.argv) > 1 else ""
    out = run(code)
    if out.get("result") is not None:
        print(json.dumps(out["result"], indent=2, default=str))
    if out.get("stdout"):
        print("[stdout]", out["stdout"], file=sys.stderr)
    if out.get("error_traceback"):
        print("[ERROR]", out["error_traceback"], file=sys.stderr)
    if out.get("success") is False:
        sys.exit(1)

if __name__ == "__main__":
    main()
