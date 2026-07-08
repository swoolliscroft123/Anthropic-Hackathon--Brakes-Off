# TASK FOR B — fetch slim Perturb-seq KO effect matrix (A is proxy-throttled)

A can reach the Perturb-seq S3 bucket but the sandbox proxy throttles it to ~0.3 MB/s,
so the 2×2.8 GB DE layers would take ~5h here. You're on a faster connection — if you
can grab this it unblocks the KO ranking immediately. It's ~7 MB of actual needed data.

## Source (public, no-auth S3)
`https://genome-scale-tcell-perturb-seq.s3.amazonaws.com/marson2025_data/GWCD4i.DE_stats.h5ad` (16.8 GB)
This AnnData has obs = 33,983 perturbation×condition rows, var = 10,282 genes,
and layers: `log_fc`, `zscore`, `adj_p_value` (each 33983×10282 float64, CONTIGUOUS).

## What A needs (slim)
Only the 25 receptor-panel genes that exist in var. Extract these columns from the
`log_fc` and `zscore` layers, plus the obs metadata, and save a small file.

The 25 present receptors (8 of our 33 aren't in this matrix): everything in
`receptor_panel_v1.json` EXCEPT CCR10, CCR9, XCR1, ACKR1, ACKR2, ACKR4, S1PR5, ITGAE.

## Recipe (if you can stream the h5ad or have the RAM)
```python
import h5py, numpy as np, pandas as pd, json
# open GWCD4i.DE_stats.h5ad (download or fsspec)
h = h5py.File("GWCD4i.DE_stats.h5ad","r")
gn = [x.decode() if isinstance(x,bytes) else x for x in h['var']['gene_name'][:]]
gni = {g:i for i,g in enumerate(gn)}
panel = list(json.load(open("receptor_panel_v1.json"))["genes"].keys())
present = [g for g in panel if g in gni]; cols=[gni[g] for g in present]
lfc = h['layers']['log_fc'][:, sorted(cols)]   # then reorder to `present`
z   = h['layers']['zscore'][:, sorted(cols)]
# reorder columns back to `present` order (h5py needs increasing cols)
order = np.argsort(cols); back=np.argsort(order)
lfc = lfc[:, back]; z = z[:, back]
# obs
def oc(n):
    o=h['obs'][n]
    if isinstance(o,h5py.Group):
        c=[x.decode() if isinstance(x,bytes) else x for x in o['categories'][:]]; k=o['codes'][:]
        return np.array([c[i] if i>=0 else None for i in k])
    return o[:]
meta = pd.DataFrame({'target':oc('target_contrast_gene_name').astype(str),
    'condition':oc('culture_condition').astype(str),
    'n_cells':np.asarray(oc('n_cells_target'),float),
    'ontarget_sig':oc('ontarget_significant').astype(str),
    'ontarget_es':np.asarray(oc('ontarget_effect_size'),float)})
np.savez_compressed("from_A_needs/ko_receptor_DE.npz",
    lfc=lfc.astype(np.float32), z=z.astype(np.float32), genes=np.array(present))
meta.to_parquet("from_A_needs/ko_receptor_DE_meta.parquet")
```
Put `ko_receptor_DE.npz` (~7 MB) + `ko_receptor_DE_meta.parquet` in `from_B/` and push.
A will do the CLR-centering + matching against your blood-referenced target.

## If you're mid-replication-cohort, that's higher priority — do this only if idle.
