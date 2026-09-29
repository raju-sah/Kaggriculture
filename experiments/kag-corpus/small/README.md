# 🌾 Kaggriculture: Match Replay Corpus & Action Trajectories (500+ Games)

## 📌 Overview
This dataset contains clean, structured tabular CSVs representing **500+ complete 720-step ladder matches** from the [Kaggle Kaggriculture Simulation Competition](https://www.kaggle.com/competitions/kaggriculture).

It is specifically curated for:
- **Imitation Learning & Behavioral Cloning (BC)**: Training supervised decision transformers, sequence models, or policy networks from top ladder playstyles.
- **Econometric & Price Elasticity Modeling**: Analyzing commodity price decay surfaces across supply gluts ($I_0 \rightarrow I_0 + 600$).
- **Multi-Unit Labor Coordination Forensics**: Studying optimal Fibonacci labor hiring thresholds and quadrant expansion timelines.

---

## 📊 Dataset Schema

### 1. `matches_meta.csv`
Summary statistics and outcomes for each complete 720-turn game:
- `episode_id`: Unique simulation match identifier.
- `player_0_team`: Team name / identifier for Seat 0 (NW quadrant spawn).
- `player_1_team`: Team name / identifier for Seat 1 (SE quadrant spawn).
- `player_0_score`: Final coin bank for Player 0 at Turn 720.
- `player_1_score`: Final coin bank for Player 1 at Turn 720.
- `winner`: Match outcome (`Player 0`, `Player 1`, or `Tie`).
- `margin`: Absolute dollar margin of victory.
- `total_steps`: Number of steps (720 turns = 30 days).

### 2. `market_orders.csv`
Detailed transaction logs for every market order submitted:
- `episode_id`: Simulation match ID.
- `step`: Turn index (\$0$ to \$719$).
- `day`: Season day index (\$0$ to \$29$).
- `player`: Player seat (\$0$ or \$1$).
- `order_type`: `BUY_SEED`, `BUY_PRODUCT`, `BUY_ANIMAL`, `SELL`, or `HIRE`.
- `item`: Commodity name (`WHEAT`, `CARROT`, `TOMATO`, `STRAWBERRY`, `MELON`, `COW`, `SHEEP`, `GOOSE`, `FERTILIZER`).
- `quantity`: Number of units ordered.

### 3. `farmer_actions.csv`
Turn-by-turn farm grid actions:
- `episode_id`: Simulation match ID.
- `step`: Turn index (\$0$ to \$719$).
- `day`: Season day index (\$0$ to \$29$).
- `player`: Player seat (\$0$ or \$1$).
- `action_verb`: `MOVE`, `TILL`, `PLANT`, `WATER`, `HARVEST`, `FEED`, `BUILD_PASTURE`, `PICKUP`, `PASS`.
- `target_or_item`: Associated item or direction.
- `quantity_or_coord`: Secondary parameter or target quantity.

### 4. `town_shop_schedules.csv`
Town shop product demand profiles and payout multipliers:
- `shop_name`: Name of town establishment (`BAKERY`, `PIZZA_SHOP`, `BRUNCH_SPOT`, etc.).
- `product_demanded`: Commodity purchased by the shop.
- `base_multiplier`: Base bonus multiplier (\$1.5\times$).
- `peak_multiplier`: Peak bonus multiplier (\$2.0\times$).

---

## 🚀 Quickstart Python Code

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load match metadata
df_meta = pd.read_csv("matches_meta.csv")
print(f"Loaded {len(df_meta)} matches!")

# Top score distribution
plt.figure(figsize=(10, 4.5))
sns.histplot(df_meta['player_0_score'], color='#0284c7', label='Seat 0 Score', kde=True)
sns.histplot(df_meta['player_1_score'], color='#e11d48', label='Seat 1 Score', kde=True)
plt.title("Score Distribution Across 500+ Kaggriculture Matches")
plt.xlabel("Final Bank Cash ($)")
plt.ylabel("Match Count")
plt.legend()
plt.tight_layout()
plt.show()
```

---

## 📜 License
This dataset is published under the **Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA 4.0)** license.
