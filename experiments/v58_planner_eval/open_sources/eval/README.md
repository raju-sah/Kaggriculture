# Licensed-source internal evaluation fixtures

These are isolated Apache-notebook snapshots for internal opponent research only. Their source notebooks, runtime files, build hashes, and provenance are recorded in [`../../../../docs/V58_LICENSED_BASELINES.md`](../../../../docs/V58_LICENSED_BASELINES.md). Ahmed V43 and the Yusuke Three-Day Shop Router contain or credit replay-derived action schedules. Do not adapt, submit, or redistribute their tapes. The attempted larger comparison was intentionally stopped after smoke comparisons showed both sources losing to frozen reset.

- `ahmed_v43/runtime/main.py`: exact extracted 321,555-byte payload, SHA-256 `919fc1d61050cd96f799979e49177ae3ac7bce98ec9835724238bea73f4a08ed`.
- `yhay_three_day/runtime/`: exact extracted notebook files; `agent.so` was compiled locally from source.
- `smoke_reset.py`: exact loader and two-seat smoke comparison on seeds 95000–95001.
- `run_panel.py`: prepared larger matrix harness; its run was stopped after four Ahmed-v43 vs v50 games. Do not treat the partial JSONL as the requested matrix.
