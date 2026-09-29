# Kaggriculture improvement — handover log

Machine-readable recovery notes for `/resume`. Newest entry last. One line per
experiment: what it was, what it scored, and what it implies.

**Standing constraints**
- **DO NOT SUBMIT TO KAGGLE.** The user submits; I only produce artifacts.
- Never use a protected/spent holdout as a fresh gate: **137501–137524,
  170001–170024, 180001–180024** are off-limits. Also spent: 160001–160060,
  150001–150015, 92600–95300.
- Free seed blocks still unused: **190001+**, **200001+**.
- Verify the standalone Kaggle loader and record the candidate SHA.
- Disk: `replay-policy none` everywhere except selective lifecycle probes.
- Judge on **official W/L and paired margin vs a matched control**, never on an
  absolute margin against a strong opponent (that mistake caused the V104 §1
  error, corrected in V104_STRATEGY_PROPOSAL.md).

**Prior-best public agent: V50, score 1233.2**, sha256
`e6b50128e023e3b9fafa1841e4cd520c5e581acb48e8628657585c18272eab2b`
(`experiments/v50_agent.py`, do not modify).

---

## V101 — one-cow swap, V92 base, exact model gate
- Candidate sha `8c572b90…`. Dev 160001–160060: +$1,392 vs V92, +$2,042 vs V50.
- Fresh holdout 170001–170024: **GATE FAIL** → NO-SUBMIT. V56 leg 8W–16L and
  3 V92 seeds below the −$2,000 no-harm floor. Trigger rate 21/24 (excellent).
- Lesson: the trigger rate reproduced, the strategy did not.

## V104 — GOOSE substitution
- **INFEASIBLE, closed.** No COOP exists before day 11 on any spent seed; the
  day-6 route places a sheep on a PASTURE. Evidence:
  `experiments/v104_commandcode/feasibility_160001.md`.
- Also carries a **corrected §1**: absolute V56 margins do not show the swap
  losing; the matched control on 180001–180024 (another worker's run) shows the
  cow swap is +$5,210 mean vs V56, margin-positive.

## V105 — two-cow swap (V101-adaptive one-cow base + second swap)
- Candidate sha `4488b263…`. Paired vs its one-cow base, spent seeds.
- vs V56: +1,089 / +2,177 mean paired delta (good). vs V92: **8W–6L–10D vs base
  12W–2L–10D**, win→loss flips on 160005/160008. **NO-GO.**
- Lesson: a second cow regresses the incumbent on outcome even when mean margin
  looks neutral. Always read W/L, not margin.

## V106 — can a public day-6 feature gate the second cow?
- **NO-GO on current data.** Inspected public features (shops, MILK/WOOL
  inventory/price, opponent day-6 herd) do **not** separate the V92 flips:
  160005/160006 and 160008/160009 share values with different outcomes. The
  one V56 day-6 replay shows opponent herd 4C/2S/0G — identical to V92's cohort
  (V56 expands later), so a day-6 herd fingerprint has nothing to key on.
- Evidence: `experiments/v106_gate_feasibility/REPORT.md`. Scoped to the
  inspected features / small sample; not a proof about the whole observation.

## V107 — V50 + one-cow no-Yarn swap (STRONGEST SO FAR)
- Base = untouched V50, no V92 overflow guard. Candidate sha **`7623988b…`**.
- Micro-check PASS: 160003 buys/picks/places 1 cow on pasture (5,3), retained,
  **+$1,638 accepted MILK**; 160001 action-identical to V50 (0 frames differ).
- Spent screen 160001–160012, both seats, paired vs matched V50 control:
  - vs **V50** (mirror): 12W–2L–10D, paired **+$1,158**
  - vs **V56**: 12W–12L, paired **+$1,614** (V50 control mean +$1,800)
  - vs **V92**: **12W–12L +$374**, paired **+$1,164** — and the control shows bare
    **V50 is 0W–24L (−$791) vs V92**, so the swap flips a losing matchup to winning
  - 7/12 trigger; the 5 non-firing seeds are exact ties everywhere; worst tail
    −$706..−$744 on one seed; zero errors.
- Gate frozen in `experiments/v107_commandcode/GATE.md` (fresh range
  **190001–190024**, V92 primary, ≥8 triggers, zero win→loss flips, no delta
  worse than −$2,000). Holdout run once — result recorded below.

## V107 fresh holdout 190001–190024 (run once, against the frozen gate)
- Result: see `experiments/v107_commandcode/REPORT.md` and
  `holdout_results.json` for the scored gate outcome. Submission remains the
  user's decision and nothing was sent to Kaggle.
