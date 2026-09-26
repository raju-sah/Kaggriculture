# Kaggriculture leaderboard refresh — 2026-09-26

The official Kaggle CLI downloaded the public leaderboard successfully. The CSV inside the archive is timestamped **2026-09-26 11:39:11 UTC** (`kaggriculture-publicleaderboard-2026-09-26T11:39:11.csv`) and contains **10,038 teams**. The [official Kaggriculture leaderboard](https://www.kaggle.com/competitions/kaggriculture/leaderboard) is dynamic; this dated CSV is the evidence for the figures below.

Rajusah (`rajucode`, team `16924472`) is **#3,450 at 1,186.5** in this snapshot. The tenth-place cutoff is **2,896.5**, a rating gap of **1,710.0**. These are the rating and rank for the team's existing Kaggle ladder submission; they are not a score for the local V59 candidate, and no submission was made during this refresh.

Compared with the September 26 01:46:39 UTC snapshot in [`V58_ELITE_RESEARCH.md`](V58_ELITE_RESEARCH.md) and [`leaderboard_snapshot_2026-09-26.json`](../experiments/v58_elite/leaderboard_snapshot_2026-09-26.json), Rajusah moved from #3,406 to #3,450 (44 places lower) and from 1,203.1 to 1,186.5 (-16.6 points). The cutoff moved from 2,904.7 to 2,896.5 (-8.2), so the gap widened by 8.4 points, from 1,701.6 to 1,710.0. The table gives the current top ten:

| Rank | Team | Rating |
|---:|---|---:|
| 1 | Boey | 3,092.6 |
| 2 | M & M & P & Q | 3,032.9 |
| 3 | Fourth Quadrant | 3,007.7 |
| 4 | DSM | 3,002.0 |
| 5 | DECEM | 2,959.6 |
| 6 | Unknown Mother-Goose | 2,931.1 |
| 7 | Azat Akhtyamov | 2,921.4 |
| 8 | Vadim Vasilenko | 2,920.9 |
| 9 | 🐚seek inspiration🐚 | 2,912.2 |
| 10 | THIRD FARM CLUB | 2,896.5 |

Reproduce with `kaggle competitions leaderboard -c kaggriculture --download -p experiments/v58_elite/leaderboard_refresh_2026-09-26T113911Z`. The raw archive is local at `experiments/v58_elite/leaderboard_refresh_2026-09-26T113911Z/kaggriculture.zip` and excluded from Git. Its SHA-256 is `cf64fdcdeb636c236adcf19f19b211b9d053a9f5fa67b91b2a16818979f89548`.
