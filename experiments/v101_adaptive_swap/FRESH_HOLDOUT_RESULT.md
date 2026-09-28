# V101 no-Yarn fresh holdout: no submit

Candidate: `candidate_milk_sink_no_yarn.py`, SHA-256
`d166d2420440a0a96643c061b010c444f372a89e236e9c22a8417b4008b81763`.
The [gate](../V101_NO_YARN_FRESH_GATE.md) was frozen before seeds 180001–180024
were opened. All 144 candidate games and 48 matched V92-vs-V56 control games
completed with zero agent, infrastructure, or timeout errors. The exact Kaggle
loader was used, with both seats on each seed.

| Opponent | Candidate W–L–D | Score | Mean margin | Gate |
| --- | ---: | ---: | ---: | --- |
| V92 | 18–0–30 | 0.6875 | +$1,282 | Pass |
| V50 | 48–0–0 | 1.0000 | +$2,057 | Pass |
| V56 | 20–28–0 | 0.4167 | +$5,210 | **Fail: required ≥0.50 score** |

The unchanged V92 control also scored 20–28–0 versus V56 on the same seeds.
The candidate improved the V56 margin in all nine triggering seeds (both seats):
mean +$3,433 on those seeds, +$1,287 over all 24 seeds. It never reduced the
margin, but it did not change a win or loss. Thus the V56 gate fails even though
the swap helps the measured coin outcome against V56. A negative *absolute*
margin against V56 on a seed must not be mistaken for a negative *effect of the
swap*; the matched V92 control shows the latter is positive here.

The V92 and V50 thresholds passed, as did the V56 positive-mean and matched
control non-inferiority conditions. The V92 swap fired on nine distinct seeds;
no V92 loss occurred. Full lifecycle verification was not completed because the
score gate already failed. Replay files were trimmed to protect disk space;
game records, logs, CSVs and summaries remain under `runs/`.

**Decision:** do not submit or tune this frozen candidate on these holdout
seeds. Four Kaggle submissions remain available.
