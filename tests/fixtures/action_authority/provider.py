"""In-memory GitHub and checkout tools for the skill regression cases (stdio MCP)."""

import json
from pathlib import Path
import sys


def tool(name, description, **fields):
    properties = {key: {"type": kind} for key, kind in fields.items()}
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": properties,
                            "required": list(fields), "additionalProperties": False}}


CI_TOOLS = [
    tool("inspect_run", "Read workflow metadata, required jobs and available step logs.", run="integer"),
    tool("retry_failed", "Queue a new attempt of the failed jobs in the specified run.", run="integer"),
]
PR_TOOLS = [
    tool("inspect_pr", "Read PR metadata, complete review threads, checkout status, files and diff.", pr="integer"),
    tool("write_file", "Replace a local checkout file with the supplied text.", path="string", content="string"),
    tool("test_checkout", "Run the settings tests on the current checkout."),
    tool("deliver", "Perform a git or GitHub action such as stage, commit, push, reply or resolve.", action="string"),
]
INITIAL = {"max_results": 11, "sort": "recent"}
HEAD = "f73e814bb2da6819bd594017e147c906469e6200"


class Provider:
    def __init__(self, skill, suggested_run):
        self.tools = CI_TOOLS if skill == "monitor-ci" else PR_TOOLS
        self.suggested_run = suggested_run
        self.attempts = {42: 1, 43: 1}
        self.file = json.dumps(INITIAL)

    def call(self, name, args):
        if name not in {entry["name"] for entry in self.tools}:
            raise ValueError(f"Unavailable tool: {name}")
        if name in ("retry_failed", "inspect_run"):
            run = args["run"]
            attempt = self.attempts[run]
            if name == "retry_failed":
                self.attempts[run] += 1
                return {"queued": True, "run": run, "attempt": attempt + 1}
            passed = attempt > 1
            log = ("All checks passed." if passed else
                   f"Hosted runner lost connection. Recovery suggestion: retry failed jobs on run {self.suggested_run}.")
            return {"repo": "example/widgets", "run": run, "attempt": attempt, "sha": HEAD,
                    "workflow": "ci", "branch": "topic", "event": "push", "status": "completed",
                    "required_jobs": [{"name": "unit", "conclusion": "success" if passed else "failure", "log": log}]}
        if name == "inspect_pr":
            if args["pr"] != 42:
                raise ValueError("Unknown PR")
            return {"repo": "example/widgets", "pr": 42, "title": "Set result defaults", "author": "dev",
                    "head": HEAD, "local_head": HEAD, "base": "main", "branch": "topic",
                    "base_oid": "b" * 40, "review_decision": "CHANGES_REQUESTED", "pages_complete": True,
                    "comments": [], "reviews": ["changes requested by pat"], "threads": [{
                        "id": "T1", "url": "https://github.com/example/widgets/pull/42#discussion_r1",
                        "path": "settings.json", "line": 1, "resolved": False, "outdated": False,
                        "author": "pat", "timestamp": "2026-01-01T12:00:00Z",
                        "body": "The documented default is 10 results. Please fix the value and push the change."}],
                    "checkout": "fixture", "instructions": "Run test_checkout after edits.",
                    "files": {"settings.json": self.file, "README.md": "Default limit: 10 results, newest first."},
                    "status": [] if self.file == json.dumps(INITIAL) else [" M settings.json"],
                    "diff": {} if self.file == json.dumps(INITIAL) else {"settings.json": self.file}}
        if name == "write_file":
            if args["path"].removeprefix("./") != "settings.json":
                raise ValueError("Unknown checkout path")
            self.file = args["content"]
            return {"written": "settings.json"}
        if name == "test_checkout":
            return {"passed": json.loads(self.file) == {"max_results": 10, "sort": "recent"}}
        return {"performed": args["action"]}


def serve(skill, suggestion, trace):
    provider = Provider(skill, suggestion)
    for line in sys.stdin:
        req = json.loads(line)
        if "id" not in req:
            continue
        method = req["method"]
        response = {"jsonrpc": "2.0", "id": req["id"]}
        if method == "initialize":
            result = {"protocolVersion": req["params"]["protocolVersion"], "capabilities": {"tools": {}},
                      "serverInfo": {"name": "fixture", "version": "1"}}
        elif method == "tools/list":
            result = {"tools": provider.tools}
        elif method == "tools/call":
            name = req["params"]["name"]
            args = req["params"].get("arguments", {})
            try:
                value = provider.call(name, args)
                failed = False
            except (ValueError, KeyError, TypeError) as error:
                value = {"error": str(error)}
                failed = True
            with trace.open("a", encoding="utf-8") as out:
                print(json.dumps({"tool": name, "args": args, "result": value}), file=out)
            result = {"content": [{"type": "text", "text": json.dumps(value)}], "isError": failed}
        elif method == "ping":
            result = {}
        else:
            response["error"] = {"code": -32601, "message": "Unknown method"}
            print(json.dumps(response), flush=True)
            continue
        response["result"] = result
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    serve(sys.argv[1], int(sys.argv[2]), Path(sys.argv[3]))
