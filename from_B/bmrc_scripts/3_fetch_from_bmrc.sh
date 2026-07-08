#!/bin/bash
# Fetch the slim result files back from BMRC to your PC, then (optionally) into
# the shared repo's from_B/ so B can pick them up. Run on your PC.
BMRC_HOST="${BMRC_HOST:-cluster4.bmrc.ox.ac.uk}"
BMRC_USER="${BMRC_USER:-hda388}"
# Where to drop the files locally (default: the shared repo's from_B/ if it exists):
DEST="${DEST:-$HOME/Desktop/Anthropic hackathon project/from_B}"
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REMOTE_DIR=$(cat "$HERE/.bmrc_remote_dir")
mkdir -p "$DEST"

echo ">> fetching result files to: $DEST"
scp "${BMRC_USER}@${BMRC_HOST}:$REMOTE_DIR/ko_receptor_DE.npz" \
    "${BMRC_USER}@${BMRC_HOST}:$REMOTE_DIR/ko_receptor_DE_meta.parquet" \
    "$DEST/"
echo ">> done. Files in $DEST:"
ls -la "$DEST"/ko_receptor_DE.*
echo
echo "If you use the git repo, then:  cd <repo> && cp '$DEST'/ko_receptor_DE.* from_B/ && git add from_B && git commit -m 'B: KO receptor DE matrix (via BMRC)' && git push"
