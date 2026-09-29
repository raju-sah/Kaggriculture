# Kaggriculture discovery research — 2026-09-19

Status: planning evidence only. No competition agent, harness, dependency, tool configuration, paid worker invocation, or Kaggle submission was created during this research.

## Executive findings

The competition objective supports the proposed emphasis on head-to-head win rate. Kaggle changes a submission's rating from wins, losses, and ties; the final coin margin does not affect the rating change. The final leaderboard will use a Bradley–Terry tournament over played episodes after roughly two additional weeks of games. Local final wealth and coin difference remain useful diagnostics, but candidate promotion should be based primarily on paired head-to-head results against a varied opponent set. [Official evaluation](https://www.kaggle.com/competitions/kaggriculture/overview/evaluation)

The smallest credible milestone is a deterministic local two-agent match followed by an exact repeat and a same-seed seat swap, with per-game status, final bank coins, W/L/D result, runtime, and replay metadata recorded. There is an important trap: the environment seed controls environment randomness, but the current built-in `random_agent` creates an unseeded `random.Random()` on every call. Matches against the built-in `"random"` opponent are therefore not reproducible merely by setting the episode seed. Use deterministic opponents or an explicitly seeded local random opponent. [Official engine source](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.py)

The repository currently contains only `.git`; there is no existing documentation convention or project code. This note therefore uses the requested fallback path.

## Current official timeline and constraints

All deadlines below are 23:59 UTC. The official page and authenticated Kaggle competition API agreed on these values on 2026-09-19:

| Event | Date |
|---|---:|
| Start | 2026-07-29 |
| Entry deadline | 2026-09-23 |
| Team merger deadline | 2026-09-23 |
| Final submission deadline | 2026-09-30 |
| Continued games / convergence period | 2026-10-01 through approximately 2026-10-15 |

The organizers reserve the right to update the timeline. [Official timeline](https://www.kaggle.com/competitions/kaggriculture/overview/timeline)

Verified competition limits and compliance boundaries:

- Maximum team size: 5.
- Maximum submissions per day: 5.
- Up to 2 final submissions may be selected. The evaluation page additionally says only the latest 2 submissions are actively tracked and used for final evaluation, while the leaderboard displays the best-scoring bot.
- External data, models, and tools are allowed when they meet the competition's accessibility, cost-reasonableness, licensing, and reproducibility requirements. Automated ML tools are allowed under the same obligations.
- Private competition-code sharing outside an official team is prohibited. Public sharing is permitted only under the competition's stated terms.
- A submission may neither receive information from outside the submission/environment nor send information out during evaluation. Development-time routing may use external services, but the evaluated agent must be self-contained and offline.
- The winner-license field is CC BY 4.0, and winners must provide a detailed, reproducible description and source/instructions sufficient for validation.
- Simulation competitions have no private leaderboard; episode replays, including actions, may be public.

These points come from the [official competition rules](https://www.kaggle.com/competitions/kaggriculture/rules). No submission action should be placed in an automated loop; it remains an explicit human approval gate.

## Evaluation and runtime

Each submitted bot first plays a self-match validation episode. A successful bot enters a rating-based matchmaking pool. Wins increase skill rating, losses decrease it, ties generally draw ratings together, and the opponent's rating affects the size of the update. Coin margin does not. Games run for 720 turns. After submissions lock, games continue for about two weeks and Kaggle produces the final leaderboard with a Bradley–Terry tournament. [Official evaluation](https://www.kaggle.com/competitions/kaggriculture/overview/evaluation)

The current official FAQ reports these submission resources:

| Resource | Limit |
|---|---:|
| Submission archive | 100 MiB |
| HDD | 8 GiB |
| RAM | 6.5 GiB |
| vCPUs | 1.6 |

Submission files are located at `/kaggle_simulations/agent/`. A single-file submission must provide a root `main.py` with an `agent` function; a multi-file `tar.gz` must also place `main.py` at its root. [Official overview / FAQ and getting-started material](https://www.kaggle.com/competitions/kaggriculture/overview)

The environment specification sets `actTimeout` to 1 second and exposes 60 seconds of remaining overage time. It uses exactly two agents. [Official environment specification](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.json)

## Authoritative environment and local availability

The competition download currently contains only `AGENTS.md` and `README.md`, both dated 2026-08-15. The executable environment comes from Kaggle's `kaggle-environments` package. The official sources are:

- [Game mechanics and observation documentation](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/README.md)
- [Local testing and submission guide](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/AGENTS.md)
- [Environment JSON specification](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.json)
- [Interpreter and built-in agents](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.py)
- [PyPI package](https://pypi.org/project/kaggle-environments/)

The latest PyPI release observed was `kaggle-environments==1.32.7`, uploaded 2026-08-15 and requiring Python 3.11 or newer. Its four Kaggriculture files exactly matched current upstream `master` byte-for-byte on 2026-09-19. The last commit touching the Kaggriculture environment directory was [`28b6d8af3ce7`](https://github.com/Kaggle/kaggle-environments/commit/28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c), immediately before that release.

| File | SHA-256 in wheel and upstream |
|---|---|
| `kaggriculture.py` | `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e` |
| `kaggriculture.json` | `a82c89c1a2315b93f39775d8e025471a01b738647c9772658368ee6b1b6f4867` |
| `README.md` | `3081e52baf8eb2da5d861acc63a3636ce29425f6bdb79a67036ba234ac4ade00` |
| `AGENTS.md` | `e1a80501a7b02a212eaac9370ada4129a64e0ee6cb3cbc790f3d77d22863fe22` |

This is strong evidence for pinning `1.32.7` in Phase 1, but Kaggle does not publish an immutable evaluator image/package lock on the competition page. A later validation submission/replay should be used to check behavioral parity before relying on large local tournaments.

Local inspection found Python 3.12.3, which satisfies the package requirement, but `kaggle_environments` is not installed in the current interpreter. Kaggle CLI 2.2.4 is installed and authenticated; no credential value was read or printed. Installing the pinned environment belongs to implementation after plan approval.

The official local entry point is:

```python
from kaggle_environments import make

env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
env.run([agent_a, agent_b])
```

Agents can be Python callables or paths to `.py` files. Built-in names are `"pass"`, `"random"`, and `"starter"`; only `starter` and `pass` are appropriate as reproducible baselines without wrapping or replacing the built-in random agent. [Official local-testing guide](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/AGENTS.md)

## Game API and visibility

Default configuration is 720 turns, 24 turns/day, 30 days, a 10×10 board per player, 3,000 starting coins, at most 10 market orders per player per turn, shed capacity 100, and weed probability 0.005 per eligible tile at end-of-day refresh. The configuration accepts an episode `seed`; the interpreter removes it from agent-visible configuration and records the resolved value in replay metadata. [Official environment specification](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.json)

An observation contains:

- `player`, framework `step`, `day`, and `hour`;
- shared `farms` for both players, including bank money, every tile, main farmer and hand positions, unlocked quadrants, and hires made today;
- shared market inventory and prices;
- shared unlocked town shops;
- a private block for only the observing player: shed inventory, seeds, and each unit's carried inventory.

Opponent farm layout, bank balance, units, crops, animals, structures, land, and hire count are legally visible. Opponent shed, seeds, and unit inventories are not. [Official observation schema](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.json#L85-L130) and [official game documentation](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/README.md#observation-format)

The action returned each turn has this shape:

```python
{
    "farmer": [op, *args],
    "hands": [[op, *args], ...],
    "market": [[op, *args], ...],
}
```

Farmer/hand operations are movement, `PASS`, `PICKUP`, `PLACE`, `DROP`, `PLANT`, `WATER`, `HARVEST`, `FERTILIZE`, `BUILD_COOP`, `BUILD_PASTURE`, `FEED`, `COLLECT_FERTILIZER`, `CARE`, and `DIG`. Market operations are `BUY_SEED`, `BUY_ANIMAL`, `BUY_PRODUCT`, `SELL`, `HIRE`, and `BUY_LAND`. Invalid actions silently no-op. Market orders are ordered and capped at 10 by default. [Official action schema](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.json#L129-L132)

The interpreter processes unit actions, interleaved market orders, town consumption, plant decay, and end-of-day refresh. At the final step it sets each reward to that player's bank money. Unsold inventory is worth zero. Winner/tie classification is therefore a comparison of the two final rewards/bank balances, while the raw rewards themselves are not a win indicator in isolation. [Official interpreter](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.py#L826-L890) and [official win/reward documentation](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/README.md#win-conditions)

## Consequences for a trustworthy tournament harness

Phase 1 should enforce these properties before any strategy conclusions:

1. Pin `kaggle-environments==1.32.7` and record the package version plus environment source hashes in every tournament report.
2. Run every environment seed twice with candidate/champion seats swapped. End-of-day randomness is stable for a seed, but player order can still change which RNG draws and market interactions each player receives.
3. Do not use the built-in `"random"` agent in reproducibility tests. Use `pass`, `starter`, or locally seeded deterministic opponents.
4. Repeat an identical game and compare final results and preferably the normalized replay. If it changes, stop before scaling the tournament.
5. Record both W/L/D and diagnostics: final coins by seat, coin difference, status, errors, wall time, seed, player assignment, opponent identity/version, and replay path/hash.
6. Keep the primary promotion target as win probability across opponents and seats. Use coin statistics to explain failures, not to overrule head-to-head results.
7. Treat crashes, timeouts, and invalid agent outputs as losses and retain their logs.

## Herdr findings

Herdr is appropriate as a visibility and terminal-lifecycle layer, and its official CLI supports workspaces, Git worktrees, panes, agent start/prompt/read/wait operations, and machine-readable responses. Worktree creation makes a real Git worktree and opens it as a grouped workspace; removal does not delete the branch. [Official CLI reference](https://herdr.dev/docs/cli-reference/) and [official agent guide](https://github.com/herdrdev/herdr/blob/master/distribution/agent-guide.md)

The installed Herdr is `0.7.4` and this session is already inside a Herdr pane (`HERDR_ENV=1`). Current stable is [`v0.9.1`](https://github.com/herdrdev/herdr/releases/tag/v0.9.1), released 2026-09-16. The syntax differs materially:

- Installed 0.7.4 starts an agent with `agent start <name> ... -- <argv>`, sends with `agent send`, and waits with `agent wait --status`.
- Current documentation separates pane creation from `agent start --kind ... --pane`, uses `agent prompt`, and supports richer `--wait`/`--until` behavior.

Do not write automation from current documentation against 0.7.4. After the harness works, make a deliberate choice: pin scripts to 0.7.4's local help, or perform a controlled upgrade and pin the newer interface. The official, release-matched Herdr agent skill is available at [the v0.9.1 source](https://github.com/herdrdev/herdr/blob/v0.9.1/skills/herdr/SKILL.md); no skill was installed or configuration changed during discovery.

Herdr's supported-agent list does not include Command Code. Command Code should therefore run directly as a child process controlled through NDJSON, or as an ordinary Herdr pane using pane-level run/read/wait operations. It should not depend on Herdr's rich coding-agent state detection.

## Command Code findings

The installed `cmd` CLI is version `1.58.0`. A read-only `cmd --list-models` returned 72 catalog entries. Catalog presence is not proof that the current Go subscription can invoke every model.

The official Go-plan page says Go has no Provider API access. CLI/headless mode is the supported automation path. It provides open models plus a limited group of premium models including GPT-5.6 Luna and Qwen Max/Plus. `CMD_ZDR=1` requests zero data retention and no prompt training for each invocation. [Official Go plan](https://commandcode.ai/docs/plans/go)

Relevant exact model IDs observed in the live CLI include:

- Kimi: `moonshotai/kimi-k3`, `moonshotai/kimi-k2.7-code`, `moonshotai/kimi-k2.7-code-highspeed`, `moonshotai/kimi-k2.6`, `moonshotai/kimi-k2.5`.
- DeepSeek: `deepseek/deepseek-v4-pro`, `deepseek/deepseek-v4-flash`, `deepseek/deepseek-v4-flash-fast`, `deepseek/deepseek-v4-flash-vision-exp`, `deepseek/deepseek-v4.1-flash`.
- GLM: `z-ai/glm-5.3-flash`, `z-ai/glm-5.3-flashx`, `zai-org/glm-5.3`, `zai-org/glm-5.2`, `zai-org/glm-5.2-fast`, `zai-org/glm-5.1`, `zai-org/glm-5`.
- Qwen: `qwen/qwen3.8-max-0902`, `qwen/qwen3.8-max`, `qwen/qwen3.8-27b`, `qwen/qwen3.8-flash`, `qwen/qwen3.8-omni-flash`, `qwen/qwen3.7-max`, `qwen/qwen3.7-plus`, `qwen/qwen3.7-flash`, `qwen/qwen3.6-max-preview`, `qwen/qwen3.6-plus`.
- OpenAI: `gpt-5.6-luna`.

The canonical way to refresh these names is `cmd --list-models`; the official registry is documented on the [available-models page](https://commandcode.ai/docs/reference/cli/models). No paid model was invoked, so actual entitlement and behavior under this account remain untested.

Headless automation can use `cmd -p <prompt> --model <id> --output-format json --max-turns <n>`. JSON output is NDJSON: zero or more event records followed by one result record containing subtype, usage, duration, and final text. Exit codes distinguish authentication, permission, rate-limit, connection, server, max-turn, no-response, and insufficient-credit failures. By default, headless mode permits reads but blocks writes and shell commands. [Official headless-mode documentation](https://commandcode.ai/docs/headless)

For Phase 1, invoke one worker only after the deterministic simulator milestone succeeds. Use read-only/plan mode for analysis. For later coding experiments, give each worker a dedicated Git worktree and a narrow permission policy; avoid blanket `--yolo`. Record model ID, CLI version, prompt hash/text, exit status, result metadata, and Git commit. Never pass credentials into a prompt or worker environment.

## Architecture review and simplification

The proposed end-state has sound boundaries: workers propose, the simulator judges, and humans approve external submission. It is too broad to build before proving the environment and tournament loop.

Recommended sequence:

1. **Determinism proof:** pinned environment, two tiny deterministic legal agents, repeat one seed, swap seats, save replay/result evidence.
2. **Tournament core:** bounded parallel matches, deterministic seed schedule, per-game records, W/L/D and coin/runtime aggregates, crash capture, and a small fixed opponent suite.
3. **Baseline economics:** implement and measure a legal baseline, then study crops/animals/market mechanics against that harness.
4. **Experiment isolation:** Git worktrees and one worker invocation with structured output; add SQLite when experiments need durable cross-run querying. JSONL/CSV is sufficient to prove the harness first.
5. **Staged promotion:** configurable 100/500/2,000-game gates with confidence estimates, opponent-stratum checks, and explicit regression rules.
6. **Orchestration:** only then add multiple worker roles and model-performance history. Add Jev after the route/decision records and promotion statistics are stable.

Herdr, multi-model debate, Jev, autonomous overnight research, opponent classifiers, and parameter optimizers should not gate the first useful tournament. Opponent adaptation is legally feasible because farm state is public, but it is lower priority than deterministic evaluation and game economics.

## First smallest end-to-end milestone

Acceptance criteria for milestone M0:

- `kaggle-environments==1.32.7` is installed in an isolated project environment and its Kaggriculture source hash is recorded.
- Two legal deterministic agents complete a 720-turn game without error.
- Re-running the same matchup, seed, versions, and seats produces the same final banks and normalized replay.
- The same seed is run with player positions swapped.
- A machine-readable record captures seed, seat assignment, agent versions, final coins, W/L/D, statuses, errors, runtime, and replay hash/path.
- An aggregate report correctly reports wins, losses, draws, win rate, mean final coins, and median coin difference over this tiny paired set.
- No Kaggle submission occurs.

Only after M0 passes should implementation expand into a tournament suite.

## Unknowns and access limitations

- Kaggle does not expose an immutable evaluator image or exact `kaggle-environments` lock in the competition materials. PyPI/upstream parity is verified, but server parity must still be checked behaviorally later.
- The official Timeline page returned template placeholders through the pages API for entry/merger dates, although the rendered official page and authenticated competition metadata both resolved them to 2026-09-23.
- Matchmaking seeds, opponent sampling, and the exact online rating-update implementation are not published in enough detail to reproduce the live leaderboard locally.
- `cmd --list-models` lists the catalog, not confirmed Go entitlements. No inference request was made, so access to each proposed worker model is still unknown.
- Herdr 0.7.4 can already manage worktrees and panes, but current documentation targets 0.9.1. Automation should wait for an explicit version decision.
- The rules permit qualifying external tools while also restricting private code sharing and data transfer. Before broad unattended worker use, retain an audit trail and verify that prompts contain only material the team is authorized to send under Kaggle's rules and the selected service terms.

