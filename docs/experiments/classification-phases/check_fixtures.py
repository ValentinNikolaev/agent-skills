"""Evaluator-only behavioral check of both sides of each supplied patch."""
from trial import revisions


def panel_failures(source):
    namespace = {}
    exec(compile(source, "panel.py", "exec"), namespace)
    failures = []
    for phase, status, wanted in [
        ("open", 200, ("record", True, "watch")),
        ("open", 403, (None, True, "fresh")),
        ("open", 503, (None, True, "retry")),
        ("watch", 200, ("record", True, "watch")),
        ("watch", 403, (None, False, "closed")),
        ("watch", 503, ("record", True, "retry")),
    ]:
        panel = namespace["Panel"](cache={"selected": "record", "other": "other record"})
        if phase == "watch":
            panel.open_result("selected", 200)
            assert panel.visible == "record"
            panel.watch_result("selected", status)
        else:
            panel.open_result("selected", status)
        actual = panel.visible, "selected" in panel.cache, panel.action
        assert panel.cache["other"] == "other record"
        if actual != wanted:
            failures.append((phase, status))
    return failures


def batch_failures(source):
    namespace = {}
    exec(compile(source, "batches.py", "exec"), namespace)
    return [(items, capacity) for items, capacity, wanted in
            [(0, 4, 0), (1, 4, 1), (4, 4, 1), (5, 4, 2)]
            if namespace["batch_count"](items, capacity) != wanted]


if __name__ == "__main__":
    for case, evaluate, expected in [
        ("K7", panel_failures, ([("open", 403)], [("watch", 403)])),
        ("R2", panel_failures, ([("open", 403)], [])),
        ("M4", batch_failures, ([(0, 4)], [(1, 4), (5, 4)])),
    ]:
        actual = tuple(evaluate(version) for version in revisions(case))
        assert actual == expected, (case, actual)
        print(case, "contract violations (base, head):", actual)
