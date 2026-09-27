"""Generate observation-driven day-level V74 macro templates from frozen V70."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "experiments/v70_capacity/agent.py"
OUT = Path(__file__).resolve().parent / "agents"
BASE_SHA = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
EXPECTED = "2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e"
if BASE_SHA != EXPECTED:
    raise SystemExit(f"Frozen V70 provenance hash mismatch: {BASE_SHA}")

TEMPLATES = [
    {"name":"v70_control", "third_land_day":None, "berry_area":12, "berry_gate":150},
    {"name":"land8_berry6_gate100", "third_land_day":8, "berry_area":6, "berry_gate":100},
    {"name":"land10_berry6_gate150", "third_land_day":10, "berry_area":6, "berry_gate":150},
    {"name":"land12_berry6_gate150", "third_land_day":12, "berry_area":6, "berry_gate":150},
    {"name":"land8_berry12_gate150", "third_land_day":8, "berry_area":12, "berry_gate":150},
    {"name":"land10_berry12_gate100", "third_land_day":10, "berry_area":12, "berry_gate":100},
    {"name":"land12_berry12_gate100", "third_land_day":12, "berry_area":12, "berry_gate":100},
    {"name":"land10_crop_only", "third_land_day":10, "berry_area":0, "berry_gate":150},
    {"name":"land8_berry6_gate200", "third_land_day":8, "berry_area":6, "berry_gate":200},
]
text = SOURCE.read_text()
if text.count(">= 150") != 3:
    raise SystemExit("V70 source gate shape changed; review generator")
old_land = "desired_unlocked = 1 + int(day >= 6)"
if text.count(old_land) != 1:
    raise SystemExit("V70 source land schedule changed; review generator")
old_straw = 'strawberry_tiles = expansion_cells if len(s["unlocked"]) > 1 and strawberry_demand and prices.get("STRAWBERRY", 0) >= 150 else ()'
if text.count(old_straw) != 1:
    raise SystemExit("V70 source strawberry tile rule changed; review generator")
old_land_gate = "if strawberry_demand and strawberry_price >= 150 and money >= land_cost + expansion_seed_budget + land_reserve:"
if text.count(old_land_gate) != 1:
    raise SystemExit("V70 source land affordability gate changed; review generator")

variants=[]
for t in TEMPLATES:
    s=text
    if t["third_land_day"] is not None:
        s=s.replace(old_land, f"desired_unlocked = 1 + int(day >= 6) + int(day >= {t['third_land_day']})")
    # Strawberry field size is part of the live layout; other available cells
    # remain in the original wheat/melon policy. Every action still re-derives
    # from current observation and visible market quotes.
    if t["berry_area"] == 0:
        land_gate = "if money >= land_cost + expansion_seed_budget + land_reserve:"
    else:
        land_gate = f"if strawberry_demand and strawberry_price >= {t['berry_gate']} and money >= land_cost + expansion_seed_budget + land_reserve:"
    s=s.replace(old_land_gate, land_gate)
    s=s.replace(">= 150", f">= {t['berry_gate']}")
    straw_rule = old_straw.replace("strawberry_tiles = expansion_cells", f"strawberry_tiles = expansion_cells[:{t['berry_area']}]")
    s=s.replace(old_straw, straw_rule)
    s=s.replace("melon_tiles = tuple(p for p in melon_tiles if p not in expansion_cells)",
                "melon_tiles = tuple(p for p in melon_tiles if p not in strawberry_tiles)")
    s=s.replace("expansion_seed_budget = 12 * STRAW_SEED_COST + 8 * WHEAT_SEED_COST",
                f"expansion_seed_budget = {t['berry_area']} * STRAW_SEED_COST + (12 - {t['berry_area']}) * MELON_SEED_COST + 8 * WHEAT_SEED_COST")
    dest=OUT/f"{t['name']}.py"
    dest.write_text(s)
    variants.append({**t,"path":str(dest.relative_to(ROOT)),"sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"base_source_sha256":BASE_SHA})
manifest={
 "objective":"screen eight original day-level macro templates plus a V70 control on spent seed 94700; own cash is primary",
 "baseline_source":"experiments/v70_capacity/agent.py",
 "baseline_sha256":BASE_SHA,
 "opponents":{"V56":"agents/v56_agent.py","V70":"experiments/v70_capacity/agent.py"},
 "screen_seeds":[94700],"expansion_seed":92802,"confirm_seed":92804,
 "promotion_gate":{"vs_v70_cash_lift_each_screen_seed":15000,"hidden_errors":0},
 "template_feasibility":{"engine":"kaggriculture 1.32.7 exact local package","cash":"land+seed purchases remain gated on live cash and $1,000 reserve; wheat/feed buys are preserved","feed":"existing live animal-count feed policy is unchanged","route":"existing state-derived worker assignment recomputes routes every observation; no fixed trajectories","deadline":"fresh crops must be watered on planting day; strawberry expansion by day 11 for yield by day 21; one-shot wheat/melon expiry rules retained"},
 "templates":variants,
}
(HERE:=Path(__file__).resolve().parent)
(HERE/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps(manifest,indent=2))
