# Kaggriculture Research Lab

This repository develops and evaluates offline agents for Kaggle's Kaggriculture simulation competition. Strategy changes are accepted only after reproducible local matches; Kaggle submission always requires explicit human approval.

## Setup

```bash
uv sync
```

The project pins Python 3.12 and `kaggle-environments==1.32.7`.

## Verify the harness

```bash
uv run python -m unittest discover -s tests -v
uv run python -m simulation.tournament \
  --agent-a agents/deterministic_wheat.py \
  --agent-b agents/deterministic_pass.py \
  --seed 20260919 \
  --repeats 2 \
  --replay-policy all \
  --output-dir experiments/runs/m0
```

The M0 command runs the seed twice in each seat assignment. It exits successfully only when all games complete and each exact repeat has the same final state and normalized replay hash. Generated reports, logs, and replays stay under `experiments/runs/` and are ignored by Git.

For larger tournaments, use named opponents and seed ranges. Full replays default to errors only; hashes and action summaries are retained for every match.

```bash
uv run python -m simulation.tournament \
  --candidate agents/deterministic_wheat.py \
  --opponent pass=agents/deterministic_pass.py \
  --opponent carrot=agents/deterministic_carrot.py \
  --seeds 1000-1049 \
  --workers 4 \
  --output-dir experiments/runs/example-panel
```

Static engine-derived economic tables can be generated with:

```bash
uv run python -m analysis.economics
```

See `docs/CURRENT_STATE.md` for the active state and next task, `docs/DECISIONS.md` for design rationale, and `docs/RESEARCH_LOG.md` for measured findings.
