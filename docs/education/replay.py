"""Replay the worked authoring or admission package through the public checkpoint CLI."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("motion", "admission"))
    parser.add_argument("journal", type=Path, help="new or interrupted private example journal")
    parser.add_argument("--skill", type=Path, default=here.parents[1] / "codex/skills/education-orchestrator")
    args = parser.parse_args()
    cli = args.skill / "scripts/workflow.py"
    path = here / "examples" / args.case / "project.json"
    bundle = json.loads(path.read_text(encoding="utf-8"))
    preset = "author" if args.case == "motion" else "admission"
    nodes = json.loads((args.skill / "references/presets.json").read_text(encoding="utf-8"))[preset]

    def run(action, *options):
        subprocess.run([sys.executable, str(cli), action, *map(str, options)], check=True)

    def latest():
        return json.loads(sorted(args.journal.glob("checkpoint-*.json"))[-1].read_text(encoding="utf-8"))

    run("check", path, "--alignment")
    if not any(args.journal.glob("checkpoint-*.json")):
        run("init", args.journal, "--preset", preset, "--project", args.case)
    if latest()["project"] != args.case:
        parser.error("journal belongs to another project")
    run("refresh", args.journal, "--bundle", path)
    for node in nodes:
        status = latest()["nodes"][node["id"]]["status"]
        if status == "passed":
            continue
        if status != "running":
            run("start", args.journal, node["id"], "--reason", "Replaying the verified reference bundle")
        refs = [f"{a['id']}@{a['revision']}" for a in bundle["artifacts"] if a["kind"] in node["outputs"]]
        run("pass", args.journal, node["id"], *refs, "--bundle", path)
    run("status", args.journal)


if __name__ == "__main__":
    main()
