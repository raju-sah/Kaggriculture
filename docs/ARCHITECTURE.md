# Architecture

## Submission boundary

`main.py` is the current champion and must remain self-contained and offline. Research tools, Kaggle APIs, Herdr, Command Code, databases, and development-only dependencies must never be imported by it.

## Local evaluation flow

```text
tournament.py
  -> fixed seeds × opponents × both seats
  -> bounded subprocess pool
  -> match_worker.py
  -> official kaggle-environments engine
  -> per-game result + optional replay + logs
  -> JSONL / CSV / aggregate statistics
```

Each match receives absolute agent paths and runs in its own Python process. This isolates crashes and prevents mutable module state from leaking between games. The cost is process startup time, currently about 4.5 seconds per game under four-way load.

## Reproducibility

Every game records:

- environment package, Python version, engine path, and engine/schema hashes;
- agent paths and file hashes;
- seed, opponent, seat assignment, and repeat number;
- final statuses, coins, W/L/D classification, runtime, and error details;
- normalized replay hash and action counts.

The Kaggle framework generates a new top-level replay UUID on every run. Replay determinism removes only that UUID before hashing and retains the raw replay hash separately.

## Tournament statistics

The primary metric is strict win rate. Draws are not wins. Reports also include rating-style score rate, decisive-game win rate, coin diagnostics, Wilson intervals, a paired-seed cluster bootstrap interval, opponent strata, and seat strata.

Candidate failures are conservatively charged as losses. When Kaggle marks both states `ERROR`, the harness uses the traceback's agent file path to attribute the originating failure. Unattributable failures remain infrastructure errors.

## Artifact retention

Per-game JSON, JSONL, CSV, hashes, action counts, and logs are lightweight and retained. Full replay bodies default to errors only because 102 replays consumed roughly 409 MiB. Determinism audits explicitly request all replays.

## Isolation and future workers

Herdr owns terminal visibility and Git worktree creation. Each future coding worker will receive a unique experiment branch/worktree. Command Code will be invoked through its headless NDJSON interface; worker output is advisory until tests and tournaments evaluate the resulting commit.

No automated path may submit to Kaggle.
