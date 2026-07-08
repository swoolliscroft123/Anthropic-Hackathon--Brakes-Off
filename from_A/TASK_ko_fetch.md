# TASK FOR B — run heavy jobs on BMRC (A has no cluster access)

A's sandbox reaches the Perturb-seq S3 bucket only through a proxy throttled to
~0.3 MB/s (5h for the full matrix), and has 8 GB RAM. You have **BMRC** — use it for
all heavy lifting. This supersedes the slim-fetch workaround; on BMRC we can just take
the full-resolution data.

## Job 1 (unblocks A's KO ranking) — extract receptor-space KO effects
On BMRC, download the DE AnnData and slice the receptor columns. It's 16.8 GB; on
BMRC's network this is minutes, and a compute node has the RAM to open it.

Source (public, no-auth):
`https://genome-scale-tcell-perturb-seq.s3.amazonaws.com/marson2025_data/GWCD4i.DE_stats.h5ad`
Structure: obs = 33,983 (perturbation × culture_condition), var = 10,282 genes,
layers = {log_fc, zscore, adj_p_value}, each 33983×10282 float64 CONTIGUOUS.

Deliverable in `from_B/`: **`ko_receptor_DE.npz`** (keys: lfc, z, padj, genes) +
**`ko_receptor_DE_meta.parquet`** (target, condition, n_cells, ontarget_sig,
ontarget_es, offtarget). Extract the 25 panel genes present in var (all of
`receptor_panel_v1.json` EXCEPT CCR10, CCR9, XCR1, ACKR1, ACKR2, ACKR4, S1PR5, ITGAE —
those aren't in this matrix). Keep panel order. ~10 MB total → fine for git.

### SLURM sketch (adjust partition/account/module to your BMRC setup)
```bash
#!/bin/bash
#SBATCH -J ko_extract
#SBATCH -p short          # or your standard CPU partition
#SBATCH -c 4
#SBATCH --mem=64G         # enough to open one 2.8GB layer + overhead
#SBATCH -t 01:00:00
module load Python/3.11    # or conda activate <env with h5py, pandas, pyarrow, numpy>
cd $SCRATCH/brakeoff
curl -sSL -o GWCD4i.DE_stats.h5ad \
  https://genome-scale-tcell-perturb-seq.s3.amazonaws.com/marson2025_data/GWCD4i.DE_stats.h5ad
python extract_ko.py     # the recipe below
```

### extract_ko.py
```python
import h5py, numpy as np, pandas as pd, json, os
h=h5py.File("GWCD4i.DE_stats.h5ad","r")
dec=lambda a:[x.decode() if isinstance(x,bytes) else x for x in a]
gn=dec(h['var']['gene_name'][:]); gni={g:i for i,g in enumerate(gn)}
panel=list(json.load(open("receptor_panel_v1.json"))["genes"].keys())
present=[g for g in panel if g in gni]; cols=[gni[g] for g in present]
srt=sorted(cols); back=np.argsort(np.argsort(cols))  # h5py needs increasing; restore panel order
def pull(name): return h['layers'][name][:,srt][:,back].astype(np.float32)
lfc,z,padj=pull('log_fc'),pull('zscore'),pull('adj_p_value')
def oc(n):
    o=h['obs'][n]
    if isinstance(o,h5py.Group):
        c=dec(o['categories'][:]); k=o['codes'][:]; return np.array([c[i] if i>=0 else None for i in k])
    return o[:]
meta=pd.DataFrame({'target':oc('target_contrast_gene_name').astype(str),
 'condition':oc('culture_condition').astype(str),'n_cells':np.asarray(oc('n_cells_target'),float),
 'ontarget_sig':oc('ontarget_significant').astype(str),'ontarget_es':np.asarray(oc('ontarget_effect_size'),float),
 'offtarget':oc('distal_offtarget_flag').astype(str)})
os.makedirs("from_B",exist_ok=True)
np.savez_compressed("from_B/ko_receptor_DE.npz",lfc=lfc,z=z,padj=padj,genes=np.array(present))
meta.to_parquet("from_B/ko_receptor_DE_meta.parquet")
print("done",lfc.shape,len(meta))
```
(`receptor_panel_v1.json` is in the repo root — copy it next to the script.)

## Job 2 (optional, parallel) — replication cohort for the target direction
If BMRC has capacity, run the SAME blood-reference recipe on a second cohort —
Zhang 2018 CRC (GSE108989) or Zheng 2017 HCC (GSE98638) — and drop
`blood_ref_delta_within_subset_REP.parquet` in `from_B/`. Lets us show the target
direction is cancer-type-robust.

## Going forward
Route ALL heavy jobs (genome-scale downloads, big pseudobulk, any >a-few-GB or
>10-min compute) to BMRC. A keeps the light analysis: CLR centering, matching engine,
ranking, figures. Log what you submit here so A knows what's in flight.
