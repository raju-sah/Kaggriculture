"""Summarize the completed frozen reset-candidate screen without dropping losses."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'experiments/runs/v57_reset_validation'
def main():
 plan=json.loads((OUT/'plan.json').read_text());rows=json.loads((OUT/'results.json').read_text())
 expected={(o,s,p) for o in plan['opponents'] for s in plan['seeds'] for p in plan['seats']}
 keys=[(r['opponent'],r['seed'],r['candidate_seat']) for r in rows]
 assert len(keys)==len(set(keys))==plan['games'] and set(keys)==expected
 assert hashlib.sha256((ROOT/plan['candidate']).read_bytes()).hexdigest()==plan['sha256']
 for r in rows:
  assert r['agents'][r['candidate_seat']]['sha256']==plan['sha256']
  assert r['agents'][r['opponent_seat']]['sha256']==plan['opponents'][r['opponent']]
 counts=lambda rs:{k:sum(r['candidate_result']==k for r in rs) for k in ('win','loss','draw','error')}
 total=counts(rows);errors=sum(bool(r['candidate_error'] or r['opponent_error'] or r['infrastructure_error'] or r['timed_out']) for r in rows)
 by={o:counts([r for r in rows if r['opponent']==o]) for o in plan['opponents']}
 report={'total':total,'execution_errors':errors,'opponents':by,'candidate_sha256':plan['sha256'],'seeds':plan['seeds']}
 (OUT/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
 text=f'''# Overnight-repair candidate: fresh screening results

The separate candidate won **{total['win']}/80 ({total['win']/80:.1%})**, with **{total['loss']} losses**, **{total['draw']} draws**, and **{errors} execution errors**. All eight requested opponents received ten games: five fresh seeds, 92800–92804, in both seats.

| Opponent | Wins | Losses | Draws |
|---|---:|---:|---:|
'''
 for o,c in by.items():text+=f"| {o} | {c['win']} | {c['loss']} | {c['draw']} |\n"
 text+='''
## Interpretation

The overnight state fix is supported by a captured-observation regression and a full-game reproduction that flips the severe seed-92718 loss into a win. This new panel screens the corrected candidate; it does **not** measure its gain over original v57, because original v57 was not rerun on these five seeds. Do not compare this percentage directly with percentages on the earlier panels.

The requested 100% win rate was not achieved. Five initial seeds are too few to establish broad robustness or top-ten readiness. The corrected artifact is suitable for further experiments, but this evidence does not support a top-ten submission claim. A new paired, broader comparison and stronger external opponents remain appropriate before promotion.

## Artifacts

- Candidate: `experiments/v57_broad/v57_reset_candidate.py`.
- Standalone archive: `experiments/v57_broad/v57_reset_submission.tar.gz` (contains only `main.py`). Extracted archive passed the captured-observation regression from an empty working directory.
- Manifest: `experiments/v57_broad/reset_manifest.json`.
- Frozen plan, game outcomes, hashes, logs and summary: `experiments/runs/v57_reset_validation/`.
- Runner: `.venv/bin/python -m experiments.v57_broad.validate_reset` (reruns the screen; not a resume command).
- Report: `.venv/bin/python -m experiments.v57_broad.report_reset` (requires all 80 unique results and verifies hashes).
- Diagnosis: [V57_RESET_DIAGNOSIS.md](V57_RESET_DIAGNOSIS.md).
- Original frozen 540-game comparison: [V57_BROAD_VALIDATION.md](V57_BROAD_VALIDATION.md).

No Kaggle submission was made. Original `agents/v57_agent.py`, its archive, and existing `main.py` were preserved. These screening seeds are now spent.
'''
 (ROOT/'docs/V57_RESET_VALIDATION.md').write_text(text)
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
