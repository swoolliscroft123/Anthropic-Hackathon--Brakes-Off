#!/bin/bash
# Run this on YOUR PC (where SSH to BMRC already works via VS Code / your key + 2FA).
# Fire-and-forget: copies the extraction scripts to BMRC and submits the SLURM job.
#
# Usage:  bash 1_run_on_bmrc.sh
#
# Edit these if your login/paths differ:
BMRC_HOST="${BMRC_HOST:-cluster4.bmrc.ox.ac.uk}"
BMRC_USER="${BMRC_USER:-hda388}"
REMOTE_DIR="${REMOTE_DIR:-/well/$BMRC_USER/ko_receptor_extract}"   # <-- set to a writable dir on BMRC (e.g. $HOME or /well/<group>/users/<you>)
# ---------------------------------------------------------------------------
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

echo ">> creating $REMOTE_DIR on $BMRC_HOST"
ssh "${BMRC_USER}@${BMRC_HOST}" "mkdir -p '$REMOTE_DIR'"

echo ">> copying scripts"
scp "$HERE/extract_ko_receptors.py" "$HERE/submit_bmrc.sh" "${BMRC_USER}@${BMRC_HOST}:$REMOTE_DIR/"

echo ">> submitting SLURM job"
JOBID=$(ssh "${BMRC_USER}@${BMRC_HOST}" "cd '$REMOTE_DIR' && sbatch --parsable submit_bmrc.sh")
echo "$JOBID" > "$HERE/.bmrc_jobid"
echo "$REMOTE_DIR" > "$HERE/.bmrc_remote_dir"

echo ">> submitted job $JOBID"
echo "   remote dir: $REMOTE_DIR"
echo "   check status:  bash 2_check_bmrc.sh"
echo "   fetch result:  bash 3_fetch_from_bmrc.sh"
