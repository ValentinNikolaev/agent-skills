"""Build the blinded packets from the pinned skill and record first-answer CLI usage."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
REV = "79dee507d8a7c8c432edc4f949780dbd9d6c5ba2"
MODEL = "gpt-6-sol"
CASES = {"K7": "panel", "R2": "panel", "M4": "batches"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(name):
    return (HERE / name).read_text(encoding="utf-8")


def source(name, headings=()):
    path = "agent-plugins/skills/" + name
    data = subprocess.check_output(["git", "show", REV + ":" + path], cwd=HERE)
    body = data.decode("utf-8")
    if headings:
        sections = re.split(r"(?=^## )", body, flags=re.MULTILINE)
        body = "\n".join(next(s for s in sections if s.startswith("## " + h + "\n"))
                         for h in headings)
    return path + "\n" + body


def revisions(case):
    name = CASES[case] + ".py"
    base = read("base/" + name).encode()
    with tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp) / name
        file.write_bytes(base)
        subprocess.run(["git", "apply", "--directory=.", "-"], cwd=tmp, check=True,
                       input=read(case + ".diff").encode())
        return base, file.read_bytes().replace(b"\r\n", b"\n")


def packet(case):
    ref = "code-review/references/"
    checks = ["Tests and verification", "Review-fix deltas"]
    docs = [source("code-review/SKILL.md"),
            source("review-retrospective/references/run-contract.md", ["Capture records"]),
            source(ref + "project-review-assets.md"), source(ref + "review-python.md")]
    if CASES[case] == "panel":
        checks += ["Classification boundaries", "Persisted shortcuts guarded at write time",
                   "Web UI and accessibility"]
        docs += [source(ref + "accessibility-checklist.md", ["Operator workflow and control state"]),
                 source(ref + "security-checklist.md", ["Authorization", "Data Protection"])]
    docs += [source(ref + "conditional-checks.md", checks), source(ref + "report-contract.md")]
    base, head = revisions(case)
    return "\n\n".join([
        "Perform a code-review --depth quick --format compact on the supplied review-fix delta. "
        "The full touched file is in the patch. The files below supply the review procedure. "
        "The project evidence consists of one contract and one patch. "
        "Work offline in one turn, verify inline and limit your report to 650 words. "
        "Only report checks you performed.",
        *docs, "Contract\n" + read(CASES[case] + "-contract.md"),
        f"One-file revisions (SHA-256, normalized LF)\nReviewed {digest(base)}\nProposed {digest(head)}",
        read(case + ".diff")]).encode()


def lock():
    return {"revision": REV, "model": MODEL, "effort": "medium", "word_budget": 650,
            "context_window": 32768, "turns": 1, "timeout_seconds": 300,
            "grader": digest(read("grading.md").encode()),
            "packets": {case: digest(packet(case)) for case in CASES}}


def save(filename, data):
    with (HERE / filename).open("x", encoding="utf-8") as out:
        out.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def review(case):
    config = json.loads(read("lock.json"))
    prompt = packet(case)
    assert lock() == config
    if (HERE / (case + ".json")).exists():
        raise SystemExit("First answer already recorded")
    cli = shutil.which("codex.cmd") or shutil.which("codex")
    args = [cli, "exec", "--json", "--ephemeral", "--ignore-user-config", "--skip-git-repo-check",
            "--sandbox", "read-only", "-m", MODEL, "-c", "model_reasoning_effort=medium",
            "-c", "model_context_window=32768", "-c", "project_doc_max_bytes=0",
            "-c", "web_search=disabled", "--disable", "memories", "--disable", "shell_tool",
            "--disable", "multi_agent", "--disable", "plugins", "--enable", "skip_host_skill_discovery", "-"]
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(args, input=prompt, capture_output=True, cwd=tmp, timeout=300)
    if proc.returncode:
        raise SystemExit((proc.stderr + proc.stdout)[-2400:].decode(errors="replace"))
    events = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    items = [e["item"] for e in events if e["type"] == "item.completed"]
    notices = [item["message"] for item in items if item["type"] == "error"]
    assert all(n.startswith("Under-development features enabled: skip_host_skill_discovery.")
               for n in notices), notices
    assert all(item["type"] in {"reasoning", "agent_message", "error"} for item in items)
    answers = [item["text"] for item in items if item["type"] == "agent_message"]
    # Some rendered links include the host's temporary user directory.
    scratch = re.compile(r"[A-Za-z]:[/\\]Users[/\\][^/\\]+[/\\]AppData[/\\]Local[/\\]Temp[/\\]tmp\w+",
                         re.IGNORECASE)
    answers = [scratch.sub("scratch", answer) for answer in answers]
    turns = [e["usage"] for e in events if e["type"] == "turn.completed"]
    assert answers and len(turns) == 1
    record = {"case": case, "packet_sha256": digest(prompt), "packet_bytes": len(prompt),
              "usage": turns[0], "commentary": answers[:-1], "answer": answers[-1]}
    save(case + ".json", record)
    print(case, turns[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["freeze", *CASES])
    action = parser.parse_args().action
    if action == "freeze":
        save("lock.json", lock())
    else:
        review(action)
