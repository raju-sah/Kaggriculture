from main import PlannerConfig
import inspect
from dataclasses import fields, is_dataclass

if is_dataclass(PlannerConfig):
    print("PlannerConfig fields:")
    for f in fields(PlannerConfig):
        print(f"  {f.name}: {f.default}")
else:
    print("PlannerConfig is not a dataclass.")
    print("PlannerConfig signature:", inspect.signature(PlannerConfig))
    print("PlannerConfig defaults:")
    for k, v in inspect.signature(PlannerConfig).parameters.items():
        print(f"  {k}: {v.default}")
