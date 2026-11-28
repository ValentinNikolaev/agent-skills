"""Prepare editor and grading packets, then join locked scores to conditions."""

import argparse
import itertools
import json
import random
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = "916e03028d18e6ed3d34dd142e37252722b39154"
CONDITIONS = ("base", "one", "two")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path, value):
    with path.open("x", encoding="utf-8") as target:
        json.dump(value, target, ensure_ascii=False, indent=2)
        target.write("\n")


def prepare(run, cases):
    base = subprocess.check_output(["git", "cat-file", "blob", BASE], cwd=ROOT).decode("utf-8")
    variants = {"base": base}
    for name in CONDITIONS[1:]:
        candidate = read(HERE / f"{name}.json")
        anchor, addition = candidate["anchor"], candidate["insertion"]
        if addition and (not anchor or base.count(anchor) != 1 or len(addition.split()) > 60):
            raise ValueError(f"Invalid insertion in {name}")
        variants[name] = base.replace(anchor, anchor + "\n\n" + addition, 1) if addition else base

    rng = random.SystemRandom()
    orders = list(itertools.permutations(CONDITIONS))
    rng.shuffle(orders)
    labels = dict(zip(rng.sample(list(CONDITIONS), 3), ["X", "Y", "Z"]))
    mapping, jobs = {}, []
    for case, order in zip(cases["cases"], orders, strict=True):
        for index, name in enumerate(order):
            job = f'{case["id"]}-{index + 1}'
            jobs.append({"id": job, "variant": labels[name], "input": case["input"]})
            mapping[job] = name
    save(run / "assignment.json", mapping)
    save(run / "editor.json", {"brief": cases["brief"], "instructions": {
        labels[k]: variants[k] for k in sorted(variants, key=labels.get)
    }, "jobs": jobs})


def blind(run, cases):
    outputs = read(run / "outputs.json")
    jobs = read(run / "editor.json")["jobs"]
    if set(outputs) != {j["id"] for j in jobs} or not all(
        isinstance(v, str) and v.strip() for v in outputs.values()
    ):
        raise ValueError("Incomplete editor outputs")
    rng = random.SystemRandom()
    identities, packet = {}, []
    for case in cases["cases"]:
        ids = [j["id"] for j in jobs if j["id"].rsplit("-", 1)[0] == case["id"]]
        choices = {}
        for letter, job in zip("ABC", rng.sample(ids, 3), strict=True):
            identities[f'{case["id"]}-{letter}'] = job
            choices[letter] = outputs[job]
        packet.append({**case, "choices": choices})
    save(run / "grade-key.json", identities)
    save(run / "blind.json", packet)


def results(run, cases):
    ids = read(run / "grade-key.json")
    arms = read(run / "assignment.json")
    outputs = read(run / "outputs.json")
    scores = read(run / "scores.json")
    if set(ids) != set(scores) or any(
        len(s) != 3 or any(type(v) is not int or v not in (0, 1) for v in s)
        for s in scores.values()
    ):
        raise ValueError("Expected three binary scores per graded output")
    for case in cases["cases"]:
        rows = {}
        for label in "ABC":
            key = f'{case["id"]}-{label}'
            job = ids[key]
            rows[arms[job]] = {"blind_label": label, "order": int(job.rsplit("-", 1)[1]),
                               "text": outputs[job], "checks": scores[key]}
        yield {"id": case["id"], "variants": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("prepare", "blind", "results"))
    parser.add_argument("run", type=Path, help="working directory for a fresh run")
    args = parser.parse_args()
    cases = read(HERE / "cases.json")
    args.run.mkdir(parents=True, exist_ok=True)
    if args.stage == "prepare":
        prepare(args.run, cases)
    elif args.stage == "blind":
        blind(args.run, cases)
    else:
        print(json.dumps(list(results(args.run, cases)), ensure_ascii=True, indent=2))
