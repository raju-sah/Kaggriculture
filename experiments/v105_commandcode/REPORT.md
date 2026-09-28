# V105 NO-GO

**Decision: NO-GO. Do not promote. No submission was made. No fresh or protected
seed was run; V50 and the V92 150-cohort were deliberately not run.**

Candidate: `experiments/v105_commandcode/candidate.py`
SHA-256 `4488b26392b69fe416fceffc6325b3b4df94fa1897a6fe8f212cd9af162ed7e0`
Base (embedded byte-for-byte): `candidate_milk_sink_no_yarn.py`
SHA-256 `d166d2420440a0a96643c061b010c444f372a89e236e9c22a8417b4008b81763`

V105 = the frozen one-cow no-Yarn candidate **plus a second sheep→cow swap** on
the other existing day-6 route. Paired design, spent seeds only, exact loader,
replay-policy `none`, ≤2 workers, zero errors throughout.

## The facts

**V56 — the target — improved (spent seeds, both seats):**

| Cohort | V105 | one-cow base | Paired delta (V105 − base) |
|---|---|---|---|
| 160001–160012 | 12W–12L, mean +5,321 | 12W–12L, mean +4,232 | mean **+1,089**, 6 better / 1 worse / 5 tie |
| 150 controls | 8W–14L, mean −1,037 | 6W–16L, mean −3,214 | mean **+2,177**, 5 better / 0 worse / 6 tie |

**V92 — the no-harm check — regressed decisively (160001–160012, both seats):**

| | V105 | base |
|---|---|---|
| Official W/L/D | **8W–6L–10D** | **12W–2L–10D** |
| Mean paired delta | **+90** (3 better / 4 worse), worst **−2,863** | — |
| Seed-level flips | win→loss on **160005** and **160008** | — |

Zero agent/infrastructure/timeout errors in every run. V92 seat-stable: True.
Both cows placed and retained on every firing seed (no unplaced-cow error).

## Why this is a NO-GO

The second cow **helps against V56 and costs four wins against V92** in the same
paired experiment on the same seeds. The mean delta (+90) is nearly neutral, but
the **official outcome record is not**: 12W–2L → 8W–6L, with two win→loss flips
on both seats (160005, 160008). V92 is the incumbent that must not regress. A
change that buys V56 margin while converting V92 wins into losses is not a safe
improvement. Margin alone would have concealed this; W/L is the deciding
evidence.

**What is established, and what is not.** What the matched paired data
establishes is purely an *opponent-dependent outcome*: the second cow is
associated with a positive paired margin against V56 (+1,089 on 160001–160012,
+2,177 on the 150 cohort) and with a negative *outcome* record against V92
(8W–6L–10D vs base 12W–2L–10D). **The economic mechanism behind that difference
is NOT established by these margins.** I have no accepted buy/sell or price
traces from these runs (replay-policy was `none`, so no per-game trades were
retained), and I am therefore not attributing the split to any supply, demand or
market-clearing effect. Any such account is a hypothesis for future work, not a
result. Note also that V56 is documented elsewhere as a heavy **producer** of
MILK/EGG (6 COW + 4 SHEEP + 7 GOOSE), so a "V56 bids milk up as a buyer" story
would in fact contradict the engine evidence; it is stated here as unsupported,
not as a finding.

Per the staging rule — stop before the 150 seeds on any decisive regression or
worst tail — I stopped here. The V92 150-cohort and the V50 check were **not
run**, and remain open.

## Next suggested intervention (not implemented, no matches run)

**Revert to the one-cow base, and re-examine the gate so the second cow is
admitted only when its marginal value is *positively* established rather than
inferred from a shop-name proxy.** This follows from the one thing the data does
establish: the second cow's effect is **opponent-dependent** — helpful against
V56, outcome-damaging against V92 — on identical seeds and identical mechanics.
The current gate admits the second cow on a name-based predicate ("a MILK-sink
shop is visible and no YARN_STORE"), which is a proxy for demand rather than a
measurement of the value the second cow actually adds. A revised gate would
instead require the V101 exact-arithmetic estimate to stay **positive at the
higher `extra=2`** setting at the moment of decision, so the second cow is only
taken when the model says two cows beat two sheep *in the state actually
observed*, not when a shop name suggests demand. Crucially, any such gate must
also carry a **no-harm bound on the V92 outcome record** (no win→loss flips),
because that is the axis that failed here and the axis a margin threshold does
not capture.

This is a design proposal, not a result: the mechanism behind the opponent
dependence is unestablished (see above), so this is one falsifiable way to test
whether the V92 regression is gate-driven. It would need the same paired
spent-seed screen, judged on **official W/L, not margin**, before anything else.
No candidate edit or match has been made, and the V105 candidate is left intact
at its recorded hash for reproducibility.

## Limits
- 23 spent seeds; V56 V/W is near coin-flip, so V56 deltas are margin-based and
  noisier than the seat-stable 150 cohort (+2,177, 5 better / 0 worse).
- V50 unrun. No readiness claim of any kind.
- Related: the V104 GOOSE line is separately closed as infeasible (no COOP
  exists before day 11; `experiments/v104_commandcode/feasibility_160001.md`).

## Artifacts
- `candidate.py`, `build_candidate.py` (byte-for-byte base embed)
- `feasibility_check.py`, `placement_check.py`, `verify_pair.py` — pre-match gates
- `screen.py` — paired runner (preflight, return-code, record-count checks)
- `runs/{v105,base}_vs_{v56,v92}[_s1|_s2]/`, `screen_results_s1.json`,
  `screen_results_s2.json`
