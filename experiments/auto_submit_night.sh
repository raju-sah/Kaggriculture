#!/usr/bin/env bash
# Overnight autonomous submission runner for Kaggriculture
set -euo pipefail

WAIT_SECONDS=${1:-12600} # 3.5 hours default
LOG_FILE="experiments/auto_submit.log"

echo "[$(date -u +%FT%TZ)] Overnight scheduler initiated. Waiting $WAIT_SECONDS seconds (~3.5 hours) before deploying submissions..." | tee -a "$LOG_FILE"
sleep "$WAIT_SECONDS"

echo "[$(date -u +%FT%TZ)] Wakeup triggered. Checking pre-submission ladder standings..." | tee -a "$LOG_FILE"
kaggle competitions submissions -c kaggriculture | tee -a "$LOG_FILE"

echo "[$(date -u +%FT%TZ)] Deploying Submission 3: ledger_lena.py..." | tee -a "$LOG_FILE"
kaggle competitions submit -c kaggriculture -f experiments/kag-corpus/refagents/ledger_lena.py -m "ledger-lena tier-7 meta line (164k bank target)" | tee -a "$LOG_FILE"

sleep 30

echo "[$(date -u +%FT%TZ)] Deploying Submission 4: broker_bea.py..." | tee -a "$LOG_FILE"
kaggle competitions submit -c kaggriculture -f experiments/kag-corpus/refagents/broker_bea.py -m "broker-bea tier-6 meta line (opportunistic wheat timing)" | tee -a "$LOG_FILE"

sleep 30

echo "[$(date -u +%FT%TZ)] Submissions deployed successfully. Final verification:" | tee -a "$LOG_FILE"
kaggle competitions submissions -c kaggriculture | tee -a "$LOG_FILE"
echo "[$(date -u +%FT%TZ)] Overnight mission complete. Quota used before daily reset." | tee -a "$LOG_FILE"
