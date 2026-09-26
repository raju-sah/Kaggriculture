# Strong-economy append overlay invariant review

`check_append_invariants.py` independently loads the frozen reset route and the append-only candidate through Kaggle's callable loader, then checks every transition observation in the retained v50 seed-94500 replay. It validates unchanged farmer/hand actions, exact base-market queue prefix preservation, the productive order subsequence (`BUY_SEED`, `HIRE`, `BUY_PRODUCT`, `BUY_ANIMAL`), and the engine's ten-order cap. For each appended action it runs the pinned Kaggriculture `_process_market` with the retained opponent order to determine whether the added WHEAT seed actually commits.

Run from the repository root with `.venv/bin/python experiments/v58_market_solver/review/check_append_invariants.py`. The captured result, including source hashes and all 67 append rows, is `append_invariant_report.json`. This is a retained-observation oracle audit, not a game evaluation and not evidence about hidden opponent actions.
