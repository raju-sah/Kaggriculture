"""Generate isolated V72 macro variants from the frozen in-house V70 source."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "experiments/v70_capacity/agent.py"
OUT = Path(__file__).resolve().parent / "agents"
BASE_SHA = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
EXPECTED_BASE = "2002db9b4bbf20c654805adc35617eb787be3e9cb64e5aae46ae1044aad3b73e"
if BASE_SHA != EXPECTED_BASE:
    raise SystemExit(f"V70 base hash mismatch: {BASE_SHA}")
text = SOURCE.read_text()
variants = []
for gate in (100, 150, 200):
    for third_quadrant_day in (8, 10, 12):
        source = text
        if source.count(">= 150") != 3:
            raise SystemExit("expected exactly three strawberry macro price gates")
        source = source.replace(">= 150", f">= {gate}")
        old = "desired_unlocked = 1 + int(day >= 6)"
        new = f"desired_unlocked = 1 + int(day >= 6) + int(day >= {third_quadrant_day})"
        if source.count(old) != 1:
            raise SystemExit("expected one V70 land expansion timing rule")
        source = source.replace(old, new)
        name = f"gate{gate}_land{third_quadrant_day}"
        dest = OUT / f"{name}.py"
        dest.write_text(source)
        variants.append({
            "name": name,
            "path": str(dest.relative_to(ROOT)),
            "sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
            "strawberry_price_gate": gate,
            "third_quadrant_unlock_day": third_quadrant_day,
            "expanded_plot_area": "V70 layout-derived wheat/melon, strawberry trigger uses expansion cells",
            "base_source_sha256": BASE_SHA,
        })
manifest = {
    "purpose": "spent-seed-only search over second-land timing and strawberry expansion price gate",
    "source_basis": str(SOURCE.relative_to(ROOT)),
    "source_sha256": BASE_SHA,
    "opponents": {"V56": "agents/v56_agent.py", "V70": "experiments/v70_capacity/agent.py"},
    "screen_seeds": [94700, 92802],
    "confirm_seed": 92804,
    "excluded_from_finalist_selection": ["gate100_land8", "gate100_land10"],
    "seat_orders": ["ab", "ba"],
    "variants": variants,
}
(Path(__file__).resolve().parent / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
