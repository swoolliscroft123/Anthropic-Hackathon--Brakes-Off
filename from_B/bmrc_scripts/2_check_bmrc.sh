#!/bin/bash
# Check the BMRC job status. Run on your PC.
BMRC_HOST="${BMRC_HOST:-cluster4.bmrc.ox.ac.uk}"
BMRC_USER="${BMRC_USER:-hda388}"
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
JOBID=$(cat "$HERE/.bmrc_jobid")
REMOTE_DIR=$(cat "$HERE/.bmrc_remote_dir")

echo ">> squeue for job $JOBID"
ssh "${BMRC_USER}@${BMRC_HOST}" "squeue -j $JOBID 2>/dev/null || echo '(not in queue — finished or not yet scheduled)'"
echo ">> tail of job log"
ssh "${BMRC_USER}@${BMRC_HOST}" "tail -n 20 '$REMOTE_DIR'/ko_receptor_extract_${JOBID}.out 2>/dev/null || echo '(no log yet)'"
echo ">> DONE marker?"
ssh "${BMRC_USER}@${BMRC_HOST}" "cat '$REMOTE_DIR'/extract_DONE.json 2>/dev/null || echo '(not done yet)'"
