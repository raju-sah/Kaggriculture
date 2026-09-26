"""Validate the packaged agent outside the repo and measure actual decision times."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import statistics
import tarfile
import tempfile
import time

ROOT=Path(__file__).resolve().parents[2]
with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
    from kaggle_environments import make
    with tempfile.TemporaryDirectory(prefix='v57-standalone-') as temp:
        with tarfile.open(ROOT/'experiments/v57/v57_submission.tar.gz') as archive:
            archive.extractall(temp,filter='data')
        spec=importlib.util.spec_from_file_location('v57_packaged',Path(temp)/'main.py')
        module=importlib.util.module_from_spec(spec)
        start=time.perf_counter();spec.loader.exec_module(module);import_seconds=time.perf_counter()-start
        timings=[]
        def timed(obs,configuration):
            start=time.perf_counter()
            result=module.agent(obs,configuration)
            timings.append(time.perf_counter()-start)
            return result
        old_cwd=Path.cwd()
        try:
            os.chdir(temp)
            env=make('kaggriculture',configuration={'seed':92503,'episodeSteps':720},debug=True)
            env.run([timed,str(ROOT/'agents/v54_agent.py')])
        finally:os.chdir(old_cwd)
result={'seed':92503,'purpose':'standalone package and timing on a previously used development seed',
        'statuses':[s.status for s in env.state],'rewards':[s.reward for s in env.state],
        'calls':len(timings),'import_seconds':import_seconds,'median_ms':statistics.median(timings)*1000,
        'p95_ms':sorted(timings)[int(.95*(len(timings)-1))]*1000,'max_ms':max(timings)*1000,
        'act_timeout_ms':1000,'cwd_was_empty_temporary_directory':True}
(ROOT/'experiments/v57/profile.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert result['statuses']==['DONE','DONE'] and result['max_ms']<1000
