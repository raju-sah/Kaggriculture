"""Generate self-contained adaptive-crop agents from the frozen reset artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments/v57_broad/v57_reset_candidate.py"
OUTPUT = ROOT / "experiments/runs/v58_policy_search/artifacts"

# Predeclared compact exhaustive grid. forecast_weight discounts expected
# demand from shop instances that have not been drawn yet; harvest_cost is the
# opportunity cost assigned to every repeat harvest after a crop's first yield.
CONFIGS = [
    {"id": "f050_h200", "forecast_weight": 0.5, "harvest_cost": 200.0},
    {"id": "f050_h400", "forecast_weight": 0.5, "harvest_cost": 400.0},
    {"id": "f100_h200", "forecast_weight": 1.0, "harvest_cost": 200.0},
    {"id": "f100_h400", "forecast_weight": 1.0, "harvest_cost": 400.0},
]

WRAPPER = r'''

# Automated v58 adaptive production family.
import copy as _search_copy
_SEARCH_FORECAST_WEIGHT = __FORECAST_WEIGHT__
_SEARCH_HARVEST_COST = __HARVEST_COST__
_SEARCH_CROPS = {
    "MELON": {"seed": 80, "first": 10, "interval": 0, "yield": 6, "ongoing": False, "base": 250},
    "TOMATO": {"seed": 50, "first": 8, "interval": 1, "yield": 4, "ongoing": True, "base": 60},
    "STRAWBERRY": {"seed": 100, "first": 10, "interval": 2, "yield": 4, "ongoing": True, "base": 120},
}
_SEARCH_SHOPS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}
_SEARCH_I0 = 10000
_SEARCH_LAST_DAY = 29


def _search_step(obs):
    raw = obs.get("step")
    return int(raw if raw is not None else int(obs.get("day", 0) or 0) * 24 + int(obs.get("hour", 0) or 0))


def _search_expected_demand(item, obs, step):
    shops = list((obs.get("town", {}) or {}).get("unlocked_shops", []) or [])
    remaining = max(0, 720 - step)
    observed = sum(1 for name in shops if item in _SEARCH_SHOPS.get(name, ()))
    demand = observed * remaining / 4.0
    # The engine unlocks at most eight shop instances on days 3, 6, ..., 24,
    # drawing uniformly with replacement from its eight named shop types.
    share = sum(1 for name, products in _SEARCH_SHOPS.items() if item in products) / len(_SEARCH_SHOPS)
    for index in range(len(shops) + 1, 9):
        unlock_step = index * 3 * 24
        if unlock_step > step:
            demand += _SEARCH_FORECAST_WEIGHT * share * max(0, 720 - unlock_step) / 4.0
    # The town center consumes one unit of every non-fertilizer product daily.
    demand += remaining / 24.0
    inventory = float(((obs.get("market", {}) or {}).get("inventory", {}) or {}).get(item, _SEARCH_I0))
    demand = max(0.0, demand - max(0.0, inventory - _SEARCH_I0))
    return demand


def _search_crop_score(crop, obs, step):
    spec = _SEARCH_CROPS[crop]
    day = int(step // 24)
    days_left = max(0, _SEARCH_LAST_DAY - day)
    first = spec["first"]
    if first > days_left:
        events = 0
    elif spec["ongoing"]:
        events = 1 + (days_left - first) // max(1, spec["interval"])
    else:
        events = 1
    output = events * spec["yield"]
    demand = _search_expected_demand(crop, obs, step)
    price = float(((obs.get("market", {}) or {}).get("prices", {}) or {}).get(crop, spec["base"]))
    expected_units_sold = min(float(output), demand)
    return expected_units_sold * price - spec["seed"] - max(0, events - 1) * _SEARCH_HARVEST_COST


def _search_best_crop(obs, step, available=None, min_seeds=0):
    eligible = []
    for crop in ("MELON", "TOMATO", "STRAWBERRY"):
        if available is not None and int(available.get(crop, 0) or 0) < min_seeds:
            continue
        eligible.append(crop)
    if not eligible:
        return "MELON"
    # Stable tie-break leaves the frozen crop in place when estimated values tie.
    return max(eligible, key=lambda crop: (_search_crop_score(crop, obs, step), crop == "MELON"))


_SEARCH_FROZEN_AGENT = agent


def _v58_adaptive_production(obs, configuration=None):
    action = _SEARCH_FROZEN_AGENT(obs, configuration)
    if not isinstance(action, dict):
        return action
    action = _search_copy.deepcopy(action)
    step = _search_step(obs)
    farm_orders = [action.get("farmer", ["PASS"]), *list(action.get("hands", []) or [])]
    melon_plant_count = sum(1 for order in farm_orders if isinstance(order, list) and len(order) > 1 and order[:2] == ["PLANT", "MELON"])
    if melon_plant_count:
        seeds = ((obs.get("private", {}) or {}).get("seeds", {}) or {})
        crop = _search_best_crop(obs, step, available=seeds, min_seeds=melon_plant_count)
        if crop != "MELON":
            for order in farm_orders:
                if isinstance(order, list) and len(order) > 1 and order[:2] == ["PLANT", "MELON"]:
                    order[1] = crop
    market = list(action.get("market", []) or [])
    best = _search_best_crop(obs, step)
    for order in market:
        if isinstance(order, list) and len(order) >= 3 and order[:2] == ["BUY_SEED", "MELON"]:
            order[1] = best

    # Preserve the base's priority and existing melon sales. Add alternate-crop
    # sales only when current actions project unsold stock in the shed.
    try:
        stock = projected_shed(obs, action)
        already = {}
        for order in market:
            if isinstance(order, list) and len(order) >= 3 and order[0] == "SELL":
                already[order[1]] = already.get(order[1], 0) + max(0, int(order[2] or 0))
        for crop in sorted(("TOMATO", "STRAWBERRY"),
                           key=lambda item: float(((obs.get("market", {}) or {}).get("prices", {}) or {}).get(item, 0)),
                           reverse=True):
            quantity = max(0, int(stock.get(crop, 0) or 0) - already.get(crop, 0))
            if quantity > 0 and len(market) < 10:
                market.append(["SELL", crop, quantity])
    except Exception:
        pass
    action["farmer"] = farm_orders[0]
    action["hands"] = farm_orders[1:]
    action["market"] = market
    return action


# Must be last callable: simulation and Kaggle execute this wrapper, not the
# older aliases retained inside the frozen source.
def _v58_adaptive_production_search_entrypoint(obs, configuration=None):
    return _v58_adaptive_production(obs, configuration)


# Kaggle's Python agent loader invokes the module-level `agent` symbol.
agent = _v58_adaptive_production_search_entrypoint
'''


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_all() -> dict[str, dict[str, str]]:
    source = BASE.read_text()
    base_hash = sha(BASE)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    built = {}
    for config in CONFIGS:
        wrapper = WRAPPER.replace("__FORECAST_WEIGHT__", repr(config["forecast_weight"]))
        wrapper = wrapper.replace("__HARVEST_COST__", repr(config["harvest_cost"]))
        path = OUTPUT / f"adaptive_{config['id']}.py"
        path.write_text(source + wrapper)
        built[config["id"]] = {"path": str(path.relative_to(ROOT)),
                               "sha256": sha(path), "frozen_base_sha256": base_hash}
    return built


if __name__ == "__main__":
    print(json.dumps({"frozen_base": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
                      "configs": build_all()}, indent=2))
