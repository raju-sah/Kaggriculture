"""Export trained LightGBM dumps as compressed JSON for the pure-Python probe."""
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "experiments/v58_validation/imitation_data"
OUT = ROOT / "experiments/v58_imitation/models"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for stem in ("action_verb", "task_label"):
        src = SOURCE / f"{stem}_model.txt"
        import lightgbm as lgb
        dump = lgb.Booster(model_file=str(src)).dump_model()
        data = json.dumps(dump, separators=(",", ":")).encode()
        dst = OUT / f"{stem}.json.gz"
        with gzip.open(dst, "wb", compresslevel=6) as f:
            f.write(data)
        print(f"{stem}: {src.stat().st_size} -> {dst.stat().st_size} bytes")

if __name__ == "__main__":
    main()
