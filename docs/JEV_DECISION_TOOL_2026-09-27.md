# Jev as a Kaggriculture decision tool

Research date: 2026-09-27. Sources below are first-party TypeSafe AI documentation and legal pages. No API call was made; the key value was never inspected.

## What Jev actually does

Jev is TypeSafe AI's **first System One model**. It evaluates a supplied `state` against independently evaluated, focused questions and returns typed answers. It is neither a multi-model debate system nor a replacement for a coding agent, game simulator, or generative reasoning model. TypeSafe explicitly says it does not write code or converse. [Introduction](https://docs.typesafe.ai/introduction), [Jev with coding agents](https://docs.typesafe.ai/introduction/coding-agents)

The official endpoint is `POST https://api.typesafe.ai/v1/systemone`, authenticated by `Authorization: Bearer <API_KEY>`. The body requires `model`, `state`, and a named `questions` map. State can be text or a JSON object/array. A question is one of: `choice` (one of up to 255 defined options, with per-option probabilities and confidence); `score` (a rubric of 2–10 ordered levels, with a weighted score, distribution, and confidence); or `noul` (yes/no probability from 0 to 1). Responses also give the resolved model ID and token usage. Questions in a call share the same state but are evaluated independently. [API reference](https://docs.typesafe.ai/api), [State](https://docs.typesafe.ai/concepts/state), [Introduction](https://docs.typesafe.ai/introduction)

The Python SDK is `typesafe-sdk` (`pip install typesafe-sdk`), with `TypeSafeClient`/`AsyncTypeSafeClient`; it reads `TYPESAFE_API_KEY` from the environment. The raw HTTP interface also works. Keep the key in the environment and out of source, logs, benchmark artifacts, and Kaggle submissions. [Python SDK](https://docs.typesafe.ai/sdk/python), [Quick start](https://docs.typesafe.ai/introduction/quickstart), [Master Customer Agreement §2.4](https://typesafe.ai/legal/mca)

## Operational limits and reliability

The currently documented stable version is `jev-1.13.0`; `jev-latest` and `jev-preview` presently resolve to it, but aliases can move. Pin `jev-1.13.0` for a reproducible experiment and record the response's resolved model. Current published limits are 64k total input tokens per request, 32k for state plus the longest question, 250k tokens/s, and 1,200 requests/min; TypeSafe says rate limits may change dynamically. Input is text only, including structured text in JSON. Official list price is $0.042 per million input tokens, with output tokens free. Account-specific availability and billing must be checked in the user's console. [Models](https://docs.typesafe.ai/models)

TypeSafe's own limitations page says Jev 1.13 struggles with numerical precision, arithmetic, counting, date comparison, multi-hop indirection, and irrelevant material in long states. It can also take adversarial content at face value. It recommends code for exact computations, concise relevant state, and explicit question criteria. A typed answer is schema-correct, **not guaranteed strategically correct**. `confidence` for Choice/Score is a summary of the returned distribution, not a measured win probability; Noul has no separate confidence field. The thresholds must be calibrated on the intended data. [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13), [Confidence](https://docs.typesafe.ai/confidence)

TypeSafe says it does not train or fine-tune its models on customer input. Its privacy policy says it does collect submitted input and retain personal data as reasonably needed for service/business purposes; zero data retention is an enterprise offering, not the default described for a regular account. Its customer agreement prohibits using its output to distill or train a model to imitate TypeSafe. Do not use Jev decisions as labels to clone Jev. [Models—data handling](https://docs.typesafe.ai/models), [Privacy Policy](https://typesafe.ai/legal/privacy-policy), [Legal overview](https://docs.typesafe.ai/legal), [Master Customer Agreement §2.3](https://typesafe.ai/legal/mca)

## Recommended Kaggriculture experiment

Use Jev **offline as a bounded hypothesis triage tool**, before adding any behavior to the competition agent. For each of 20–40 representative local replays, prepare a compact, non-secret state with *code-computed* facts: day, land and herd counts, liquid cash, accepted sales by product, idle staff turns, movement turns, unplanted available cells, and the next known product demand. Ask a Choice question such as “Which single bottleneck most plausibly explains the observed lost revenue in this state?” with fixed options `capital`, `feed`, `planting_capacity`, `harvest_capacity`, `market_demand`, `worker_travel`, and `none_of_these`. Ask separate Noul questions for qualitative risks such as whether the documented action pattern suggests a staffing bottleneck. Store only the response model ID, typed answers, uncertainty, and a replay identifier; exclude the key and request headers.

Then independently verify each Jev-selected bottleneck against exact simulator counters and one-variable policy interventions. Compare Jev-guided prioritization with the current human/code diagnosis on **held-out** games, using actual final cash, accepted sales, invalid actions, and paired wins. If it identifies useful failures, encode the resulting causal rules or improvements in ordinary agent code. Do not assume live Jev calls are allowed during Kaggle evaluation; inspect competition execution/network rules before considering that design. This experiment uses the model for the qualitative, closed-set judgment the documentation describes, while exact economics and action legality remain in code. [How to build with TypeSafe](https://docs.typesafe.ai/concepts/how-to-build-with-system-one), [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13), [Jev with coding agents](https://docs.typesafe.ai/introduction/coding-agents)

An alternative, if a directly measurable tactical judgment exists, is to test a small Choice over already-legal, code-generated tactical options in a local shadow evaluation. Every Jev choice must be compared with a no-Jev baseline under identical seeds and both seats before promotion. Avoid asking it to calculate the best move from raw numeric game state: that directly hits its documented weak points. [API reference](https://docs.typesafe.ai/api), [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13)

## Implemented first offline probe

The three replay-reconciled seed-94700 case studies are in [`jev_case_studies.json`](../experiments/v75_joint/jev_case_studies.json), with SHA-256 values of the actual replay files. [`jev_triage.py`](../experiments/v75_joint/jev_triage.py) sends one official API request per case with pinned `jev-1.13.0`, one closed-set Choice for the primary mechanism, and two independent four-level Scores for service and liquidity stress. It checks the response shape, returns only expected fields, and makes at most three attempts with bounded backoff on retryable HTTP errors. It never runs inside the competition agent. The case studies contain observations and no model-produced training labels. The current execution environment does not expose a usable `TYPESAFE_API_KEY`, so only dry runs and mocked tests have been executed; there are no live Jev answers yet.

From the project root, inspect a key-free request and run the mocked contract tests:

```sh
.venv/bin/python experiments/v75_joint/jev_triage.py --case third_land_macro_94700 --dry-run
.venv/bin/python -m unittest tests.test_jev_triage -v
```

When `TYPESAFE_API_KEY` is available to the process, run the three-case offline call with:

```sh
.venv/bin/python experiments/v75_joint/jev_triage.py
```

The script never writes the key or request headers to a file or output. Treat returned rankings as hypotheses, then use exact replay settlement and paired game interventions to decide whether to change policy. [API reference](https://docs.typesafe.ai/api), [Confidence](https://docs.typesafe.ai/confidence)

## Prior project trials

The [2026-09-23 project research log](RESEARCH_LOG.md) describes three full **browser** Jev seasons: a headed passive run with a reported 1,868 coins, a headed v2 active loss, and a headless v3 run with 2,260 coins. The saved output supports a narrower conclusion:

| Saved run | Recoverable evidence | Limit |
| --- | --- | --- |
| [`30d-seed4348`](../experiments/jev-live/runs/30d-seed4348/) | Its `turns.jsonl` contains 720 entries through day 30, turn 24, mostly `PASS` (537) and `HARVEST` (180). Its separate `state_last.json` snapshot says day 30/turn 24 and `money` = `[2998, 2998]`. | The research log's 1,868 figure is not present in these saved records; the snapshot precedes the final turn log and cannot verify the reported terminal score. Opponent and winner are unidentified. |
| [`30d-v2`](../experiments/jev-live/runs/30d-v2/) | Its `turns.jsonl` has 720 entries through day 30, turn 24; `finish.out` confirms the last browser turns. The research log calls it an active loss. | The saved turn log and finish output lack both terminal coin values, a named opponent, and a winner field. The loss and margin cannot be independently reconstructed from these files. |
| [`30d-headless1`](../experiments/jev-live/runs/30d-headless1/) | Its `turns.jsonl` has 720 entries through day 30, turn 24. The last recorded fields are `money1=2260` and `money2=3455`; `driver.out` also ends at 2,260 for the displayed side. The research log calls this headless v3. | The first recorded side is behind the second by 1,195 coins at the terminal snapshot, but the files do not name the opponent or provide an explicit winner/seat identity. |

These are historical interactive browser runs with differing driver policies. They are useful evidence that the Jev-powered browser driver completed seasons, and that at least the saved headless run did not surpass the other recorded side in coins. They are **not** paired exact-engine Kaggle tournament games: the outputs do not establish fixed opponent identities, matched seats and seeds, or a leaderboard score. They cannot demonstrate a win-rate or top-ten readiness. No old key material or live API was used for this audit.
