# V59 early-Yarn sheep mix gate: no-go

## Decision

Stop this branch. The isolated early-Yarn/high-Wool rule passed its replay
fidelity checks, but it produced no measurable difference from the frozen v57
reset on the only fresh paired seed. No v54 or v56 games were run. This is not
a submission candidate and says nothing about final holdout performance.

## Signal and implementation

The teacher replay review found a specific lead: on seed 95508, YARN_STORE
unlocked on days 6 and 18 while WOOL stayed above $200. The frozen route bought
7 geese and 4 sheep and sold 72 wool; v50 bought 11 sheep and sold 379 wool.
Seed 95518 showed the early-Yarn/high-Wool regime and another large deficit.
On seed 95501, YARN_STORE arrived on day 24 after wool had collapsed, and the
frozen goose-heavy route won. This motivated a narrow gate: days 1–11, YARN_STORE
unlocked, WOOL at least $180.

`experiments/v59_route_rules/mix_gate/candidate_isolated.py` overlays the frozen
reset. It replaces at most one goose purchase with a sheep only after the
existing sheep count reaches four, and routes only the marked extra sheep to a
vacant pasture. It preserves all ordinary worker actions. The candidate SHA-256
is `50430cd46641f5b2b26b5b99a2fe4738513f8a9186b011f8620e8c14dbd94a20`; the
frozen reset SHA-256 is
`4173479fe1f80d031d570d1ea23b694dfe86e1d162317a4c9c7df0058a40208e`.

The isolated implementation passed 5 focused tests, including the Kaggle loader
schema and baseline sheep-job preservation. Replay audit on spent seeds found:

- Seed 95501: byte-identical output to frozen reset on all 720 frames.
- Seed 95508: two one-goose-to-one-sheep market substitutions, no worker action
  changes, and no baseline sheep route changes.
- Seed 95518: byte-identical output on all 720 frames.

The substitutions on 95508 occurred after the observed gate became active; the
seed 95518 policy trace never reached an eligible extra purchase. A direct
replay audit of both candidate-seat replays on fresh seed 95611 found the gate
active for 60 frames in each seat order, but zero changed actions or orders.

## Game screen

All games used the pinned Kaggle engine 1.32.7, engine SHA-256
`bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`. The
fresh paired screen used seed 95611 against v50 in both seat orders, with the
frozen reset as the matched control:

| Candidate | Seat orders (candidate coins; margin) | Record | Errors/timeouts |
|---|---|---:|---:|
| Isolated gate | AB: 72,608; −27,935. BA: 72,608; −27,935 | 0–2 | 0 / 0 |
| Frozen reset | AB: 72,608; −27,935. BA: 72,608; −27,935 | 0–2 | 0 / 0 |

The paired incremental coin-margin delta was exactly $0 in both seat orders.
Candidate and control report files are under
`experiments/v59_route_rules/mix_gate/dev95611_v50_isolated/` and
`experiments/v59_route_rules/mix_gate/control95611_v50/`.

Seed 95610 is spent diagnostic evidence only. Its first candidate was
contaminated: it rerouted baseline sheep jobs instead of isolating only extra
sheep. Against v50 it scored 0–2 with mean candidate coins $62,452 and mean
margin −$3,113. The matched frozen reset scored 2–0 with mean coins $62,136 and
margin +$14,064, a −$17,177 per-seat paired margin change. Because the candidate
was contaminated, these results do not estimate the isolated rule's effect;
they are recorded here to prevent accidental reuse as fresh evidence. The
contaminated file is preserved as
`experiments/v59_route_rules/mix_gate/candidate_contaminated_41bdb1d3.py`.

## Scope and artifacts

No additional seed was run after the matched 95611 pair. Seed 95610 is not
reused. No v54/v56 screen, main-file edit, submission, or final-holdout run was
made. The tests are in
`experiments/v59_route_rules/mix_gate/test_isolated.py`; replay fidelity details
are in `experiments/v59_route_rules/mix_gate/isolation_audit.json`.
