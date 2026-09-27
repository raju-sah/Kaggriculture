# V67 alternative: selective crop expansion trial

## Result

This branch does **not** beat V66 and is rejected as an improvement. The exact-loader paired seat run on the already-spent seed 94700 produced $36,010 and $35,936 for V67 alternative, against $133,107 and $133,144 for V56. It lost both seats with no runtime or infrastructure errors. V66's existing seed-94700 paired run finished at $44,930 per seat. No new seed was used and no Kaggle submission was made.

| Evidence | Seat 0 | Seat 1 |
|---|---:|---:|
| V67 alternative ending coins | 36,010 | 35,936 |
| V56 ending coins | 133,107 | 133,144 |
| V67 alternative result | loss | loss |

Exact-loader artifacts are in `experiments/v67_alternative/spent94700_v56/`; tournament report: `report.json`; per-game records: `games.jsonl`; normalized replays: `replays/`.

## Design tested

Starting from submitted V66 source (SHA-256 `d82c430c9562b6b213b92899d4df59aa9b9b58bcc8bdf3522b9e819da03e083d`), this independent branch made later quadrants stable crop zones, split added cells between wheat and melon, and gated land purchase on cash above a working reserve. Its hire ladder rose from five to seven, eight, and nine hands using land count and cash reserves as a coarse proxy for backlog; it did not implement a sufficiently strong task-throughput gate. Seed targets scaled to the derived crop slots. The strategy did not add livestock to the new acreage.

On the representative seat-0 replay, land purchases occurred by days 8, 19, and 20. The agent had 13 wheat and 13 melon plants at day 12, but the extra late acreage was not converted into season-long production. It ended with 123 SELL actions against 132 for V66 and 309 for V56. Plant actions were 122 against V56's 229; hires were 204 against V56's 289. The additional hectares increased travel and servicing demand faster than sale throughput. This agrees with the local V67 original-rebuild experiment, which also found full-acreage expansion reduced output.

The next useful decision point is to gate expansion against *observed harvest and sale throughput*, not cash balance alone, and to preserve the original production plan unless the first plot's backlog is being cleared. This trial does not establish that any expanded strategy can reach $100k.

## Provenance and verification

The agent is `experiments/v67_alternative/agent.py` (SHA-256 recorded below). It contains no replay tape or third-party source. The paired match used `simulation.tournament` and the repository's Kaggle Environment 1.32.7 exact loader; both candidate seats completed. No fresh seed, official submission, or new Kaggle score was used.

```text
agent sha256: 780728807b764d4e3d13125dfa69aef9e7a6643acdb23804f4720c83e894031f
V56 sha256: d9e9670921b62afedfa8cbc7086d2a2ec19e153ee26006cef477eadd462bd19c
engine sha256: bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e
```
