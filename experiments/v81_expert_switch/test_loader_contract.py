"""Loader-faithful checks for an agent file.

kaggle_environments.agent.get_last_callable execs the raw file into a fresh
empty dict and returns `[v for v in env.values() if callable(v)][-1]`. Any test
that loads the file with importlib instead will bind the entrypoint by name and
silently miss a mismatch between the intended entrypoint and the callable the
real loader would select.

These checks reproduce the loader exactly. Run:

    .venv/bin/python experiments/v81_expert_switch/test_loader_contract.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / "experiments/v81_expert_switch/hybrid.py"
ENTRYPOINT = "_kaggle_submission_entrypoint"


def last_callable(path):
    """Exactly what kaggle_environments.agent.get_last_callable selects."""
    env = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), env)  # noqa: S102
    return [name for name, value in env.items() if callable(value)][-1]


def main() -> int:
    failures = []
    selected = last_callable(CANDIDATE)
    print(f"loader-selected callable: {selected}")
    if selected != ENTRYPOINT:
        failures.append(
            f"loader would call {selected!r}, not {ENTRYPOINT!r}; every turn would be PASS"
        )

    # The same contract for the V80 candidate, which had the same latent shape.
    v80 = ROOT / "experiments/v80_wool_route/candidate.py"
    if v80.exists():
        v80_selected = last_callable(v80)
        print(f"V80 loader-selected callable: {v80_selected}")
        if v80_selected != ENTRYPOINT:
            failures.append(f"V80 loader would call {v80_selected!r}")

    # And the frozen sources, which must remain correct.
    for rel in (
        "experiments/v57_broad/v57_reset_candidate.py",
        "experiments/v50_agent.py",
    ):
        name = last_callable(ROOT / rel)
        print(f"{Path(rel).name} loader-selected: {name}")
        if name != ENTRYPOINT:
            failures.append(f"{rel} loader would call {name!r}")

    if failures:
        print("\nFAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("\nPASS: every file's last callable is the submission entrypoint")
    return 0


if __name__ == "__main__":
    sys.exit(main())
