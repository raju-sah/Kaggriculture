#!/bin/bash
set -e

mkdir -p experiments/runs/v56_final_tests
echo "Starting tournaments..."

opponents=(
    "v55=agents/v55_agent.py"
    "v54=agents/v54_agent.py"
    "v53=agents/v53_agent.py"
    "v52=experiments/v52_agent.py"
    "v51=experiments/v51_agent.py"
    "v50=experiments/v50_agent.py"
    "v48=experiments/v48_agent.py"
)

for opp in "${opponents[@]}"; do
    name=$(echo $opp | cut -d'=' -f1)
    echo "Running v56 vs $name..."
    uv run python -m simulation.tournament --candidate agents/v56_agent.py --opponent $opp --repeats 5 --workers 4 --output-dir experiments/runs/v56_final_tests/$name > experiments/runs/v56_final_tests/${name}_out.txt 2>&1
    echo "Finished $name"
    grep -E '"win_rate":|wins"|losses"' experiments/runs/v56_final_tests/$name/report.json | head -n 4
done
echo "All done!"
