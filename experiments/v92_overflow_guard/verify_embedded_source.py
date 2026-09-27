"""V92 packaging verification: the candidate must run from an empty temp cwd.

Checks, in order:
  1. the embedded V50 text equals the real experiments/v50_agent.py byte-for-byte;
  2. `kaggle_environments.agent.get_last_callable` selects the submission
     entrypoint (it returns the LAST module-level callable, so a helper defined
     after the entrypoint would be selected instead);
  3. a full 720-step game runs with ONLY this file copied into an empty temp
     directory, with the repository unreachable from the working directory.

Usage:  .venv/bin/python experiments/v92_overflow_guard/verify_embedded_source.py
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/home/raju/AI-ML Projects/Kaggle Competition/Kaggriculture")
CANDIDATE = ROOT / "experiments/v92_overflow_guard/candidate.py"
V50 = ROOT / "experiments/v50_agent.py"
V56 = ROOT / "agents/v56_agent.py"
ENTRYPOINT = "_kaggle_submission_entrypoint"


def check_embedded():
    import base64
    v50 = V50.read_text()
    text = CANDIDATE.read_text()
    ns = {"__name__": "probe"}
    exec(compile(text.split("_V50_SOURCE_B64 = (")[0], "probe", "exec"), ns)
    b64 = text.split("_V50_SOURCE_B64 = (")[1].split(")")[0]
    embedded = "".join(part.strip().strip('"') for part in b64.splitlines())
    decoded = base64.b64decode(embedded).decode("utf-8")
    if decoded != v50:
        print("FAIL: embedded V50 text does not match experiments/v50_agent.py")
        print(f"      embedded sha {hashlib.sha256(decoded.encode()).hexdigest()}")
        print(f"      real     sha {hashlib.sha256(v50.encode()).hexdigest()}")
        return False
    print(f"PASS: embedded V50 decodes to experiments/v50_agent.py byte-for-byte "
          f"(sha256 {hashlib.sha256(decoded.encode()).hexdigest()[:16]})")
    return True


def check_entrypoint():
    from kaggle_environments.agent import get_last_callable
    fn = get_last_callable(CANDIDATE.read_text(), None, str(CANDIDATE))
    name = getattr(fn, "__name__", str(fn))
    if name != ENTRYPOINT:
        print(f"FAIL: loader selects {name!r}, expected {ENTRYPOINT!r}")
        return False
    print(f"PASS: get_last_callable selects {name}")
    return True


def check_isolated_game():
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / "candidate.py"
        shutil.copy(CANDIDATE, dst)
        opp = Path(tmp) / "v56.py"
        shutil.copy(V56, opp)
        script = (
            "import json,sys\n"
            "from kaggle_environments import make\n"
            "env=make('kaggriculture',configuration={'episodeSteps':720,'seed':92802},debug=True)\n"
            "env.run(['candidate.py','v56.py'])\n"
            "r=env.toJSON()\n"
            "st=r['steps']\n"
            "acts=[ (s[0].get('action') or {}) for s in st[1:] ]\n"
            "nonpass=sum(1 for a in acts for u in [a.get('farmer')]+list(a.get('hands') or []) if u and u[0]!='PASS')\n"
            "print(json.dumps({'rewards':[s.get('reward') for s in st[-1]],'nonpass':nonpass}))\n"
        )
        proc = subprocess.run([sys.executable, "-c", script], cwd=tmp,
                              capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            print("FAIL: isolated game did not complete")
            print(proc.stderr[-1500:])
            return False
        line = proc.stdout.strip().splitlines()[-1]
        out = json.loads(line)
        rewards = out["rewards"]
        if rewards[0] is None or rewards[0] <= 3000:
            print(f"FAIL: candidate did not play (rewards {rewards})")
            return False
        print(f"PASS: isolated full game from empty temp dir; candidate reward {rewards[0]:.0f}, "
              f"opponent {rewards[1]:.0f}, {out['nonpass']} non-PASS actions")
        return True


def main():
    ok = check_embedded() and check_entrypoint() and check_isolated_game()
    print("\n" + ("ALL CHECKS PASSED" if ok else "CHECKS FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
