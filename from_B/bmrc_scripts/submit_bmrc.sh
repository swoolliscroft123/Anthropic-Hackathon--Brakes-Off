#!/bin/bash
#SBATCH --job-name=ko_receptor_extract
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err
#SBATCH --time=02:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=4
# NOTE: partition/account are left unset — add "#SBATCH -p <partition>" and
# "#SBATCH -A <account>" for your BMRC allocation if the cluster requires them.

set -euo pipefail
cd "${SLURM_SUBMIT_DIR:-$PWD}"

# --- environment: adjust to your BMRC module/conda setup -------------------
# Option A (module system):
#   module load Python/3.11 || module load python/3.11
# Option B (conda):
#   source ~/miniconda3/etc/profile.d/conda.sh && conda activate base
# Ensure numpy, pandas, h5py, pyarrow are importable. Quick check + pip fallback:
python3 - <<'PY' || pip install --user numpy pandas h5py pyarrow
import numpy, pandas, h5py, pyarrow
PY

echo "host: $(hostname)  start: $(date)"
python3 extract_ko_receptors.py --outdir "$PWD"
echo "end: $(date)"
