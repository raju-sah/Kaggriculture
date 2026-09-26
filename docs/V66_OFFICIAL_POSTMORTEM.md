# V66 official Kaggle postmortem

## Finding

Submission **56583862** is complete with current public score **492.1**. The first postmortem query showed 506.5; Kaggle later reported 492.1 while the submission remained complete. Kaggle's `competitions episodes` endpoint returned five public episodes and one validation/self-play episode. All six completed replays are available locally; the five public games give four decisive outcomes and one near draw: V66 won twice and lost three times, with the loss margins including two roughly $50k deficits. The endpoint currently exposes only six episodes for this submission, so an eight-match official sample cannot be produced from its records.

The earliest recurring, controllable bottleneck is the planner's **permanent refusal to expand land**. `original_planner.py` has no `BUY_LAND` order in `_bridge_market`; its opening-layout function takes only the first unlocked quadrant. Consequently V66 stayed in NW and capped its intended opening at five pasture plots, two coop plots, and twenty crop plots for every public match. Three opponents bought land twice and unlocked NW, NE, and SW. In the two same-seed matches where those opponents beat V66, expansion accompanied a **$50,282** and **$51,943** final-cash advantage. The third expansion matchup was nearly even (+$429 for V66). The replay comparison is observational rather than an isolated causal experiment, but the hard-coded land ceiling is directly verified and the more-than-$20k consequence is credible from the same-game outcomes.

The exact source hash is `d82c430c9562b6b213b92899d4df59aa9b9b58bcc8bdf3522b9e819da03e083d`; the submitted bundle and `original_planner.py` have that same SHA-256. The replay engine reports **module version 1.32.7** for all six games. As a source-to-runtime check, calling the exact source on each V66 observation reproduces the following replay action on **719/719 noninitial turns in every episode**, including the match where V66 was seat 1.

## Public-game comparison

| Episode | Seed | V66 seat | V66 cash | Opponent cash | Opponent | Opponent land / plants issued | V66 result |
|---:|---:|---:|---:|---:|---|---|---:|
| 113766768 | 585360995 | 0 | $27,581 | $77,863 | sunchang71 | NW+NE+SW / 131 | −$50,282 |
| 113767976 | 182741576 | 1 | $54,831 | $106,774 | Facouse | NW+NE+SW / 194 | −$51,943 |
| 113769161 | 2012648151 | 0 | $57,524 | $26,384 | Peter Mugoya | NW only / 31 | +$31,140 |
| 113770383 | 267154532 | 0 | $37,209 | $42,306 | nasa Furiy | NW only / 51 | −$5,097 |
| 113771594 | 1764493568 | 0 | $48,603 | $48,174 | Mohamed Judi | NW+NE+SW / 233 | +$429 |

The V66 policy is strikingly invariant: it ended every public match with the same seven-animal herd (2 cows, 3 sheep, 2 geese), five hands, and no live crop tiles. In those five matches it issued 72–79 plant actions, 174–177 harvest actions, 322–339 water actions, 127–139 sell orders, and 124–128 wheat-product buy orders (148–150 units total). Its seller orders moved about 482 product units in the representative losses, while the expanded opponents moved substantially more: in episode 113766768, for example, sunchang71 issued 545 sell orders for 4,409 units and 279 wheat-feed buys for 967 units; V66 issued 139 sell orders for 482 units and 128 feed buys for 150 units. (These are replay action quantities, not a reconstructed cash ledger.)

That pattern points to a scale/throughput limit as well as a land limit. V66 repeatedly spends worker actions feeding and tending a small fixed herd and has no expansion phase that can add crop capacity or production labor. On episode 113766768, V66 issued 2,547 movement actions against the opponent's 4,119, while the opponent also issued 337 harvest, 851 water, and 131 plant actions against V66's 174, 324, and 72. In episode 113767976 V66's action mix was the same, while Facouse issued 386 harvest, 986 water, and 194 plant actions. These traces show that the difference was persistent work capacity and production, not a one-off terminal sale.

## Local control evidence

The archived exact-loader, spent-seed-94700 match against v56 also lost both seats: V66 finished at **$44,930** against **$129,477**, a **−$84,547** margin each time, with no candidate errors or timeouts. This corroborates the official production gap, but it is only one seed and does not establish a general win rate. No fresh seed was used in this postmortem.

## Scope and artifacts

The compact derived replay manifest at [`experiments/v66_postmortem/episode_summary.json`](../experiments/v66_postmortem/episode_summary.json) records episode IDs, seeds, seats, rewards, end-state plots/herds/workers, action counts, market quantities, module versions, and SHA-256 hashes of all replay files. [`analyze.py`](../experiments/v66_postmortem/analyze.py) regenerates it from the raw downloads. Raw Kaggle replays and the one successfully retrieved agent log are under the ignored `experiments/kaggle/v66_postmortem/` directory; raw game traces are not included in the compact artifact.

Kaggle CLI showed these five public games plus validation episode **113765357** (self-play, 43,656–43,656). The other four public games span both seats and both outcomes. The public sample is small and not opponent-controlled; opponent identity does not prove any opponent is one of v48–v56. The stronger v56 local comparison is kept separate from official evidence. This report recommends testing an actual economic land-expansion/production phase next; it does not claim top-ten readiness or the requested 10/10 benchmark.
