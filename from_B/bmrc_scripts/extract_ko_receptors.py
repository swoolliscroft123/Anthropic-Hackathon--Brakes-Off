#!/usr/bin/env python3
"""
Extract the 25 receptor-panel columns from the Marson 2025 genome-scale
Perturb-seq DE matrix (GWCD4i.DE_stats.h5ad) on BMRC, where the S3 bucket is
reachable at full speed. Produces the slim files Session A needs.

Outputs (written next to this script's --outdir):
  ko_receptor_DE.npz        : lfc (33983x25 f32), z (33983x25 f32), genes (25,)
  ko_receptor_DE_meta.parquet: obs metadata (target, condition, n_cells, ontarget_sig, ontarget_es)

Run on a BMRC compute node (see submit_bmrc.sh). Needs: numpy, pandas, h5py, pyarrow.
"""
import os, sys, json, time, argparse
import numpy as np, pandas as pd, h5py

S3_URL = "https://genome-scale-tcell-perturb-seq.s3.amazonaws.com/marson2025_data/GWCD4i.DE_stats.h5ad"

# 33-gene panel (fixed order). 25 are present in this matrix; 8 are absent
# (CCR10, CCR9, XCR1, ACKR1, ACKR2, ACKR4, S1PR5, ITGAE) and are skipped.
PANEL = ["CXCR3","CXCR6","CCR5","CXCR4","CCR8","CCR2","CCR6","CX3CR1","CCR7","CXCR5",
         "CCR4","CCR10","CCR9","CCR1","CCR3","XCR1","ACKR1","ACKR2","ACKR3","ACKR4",
         "GPR183","GPR15","S1PR1","S1PR4","S1PR5","SELL","SELPLG","ITGA4","ITGAE",
         "ITGAL","ITGB1","ITGB2","ITGB7"]

def read_obs(h, name):
    o = h['obs'][name]
    if isinstance(o, h5py.Group):  # categorical
        cats = [x.decode() if isinstance(x, bytes) else x for x in o['categories'][:]]
        codes = o['codes'][:]
        return np.array([cats[i] if i >= 0 else None for i in codes], dtype=object)
    return o[:]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--h5", default=None,
                    help="Path to a local GWCD4i.DE_stats.h5ad. If omitted, downloads from S3 to --outdir.")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--keep-h5", action="store_true", help="Keep the downloaded 16.8 GB h5ad.")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    h5path = args.h5
    if h5path is None:
        h5path = os.path.join(args.outdir, "GWCD4i.DE_stats.h5ad")
        if not os.path.exists(h5path):
            print(f"[{time.strftime('%H:%M:%S')}] downloading 16.8 GB h5ad from S3 ...", flush=True)
            # BMRC has fast unthrottled egress; a plain download is fine here.
            import urllib.request
            t = time.time()
            urllib.request.urlretrieve(S3_URL, h5path)
            print(f"  downloaded in {time.time()-t:.0f}s -> {h5path}", flush=True)
        else:
            print(f"reusing existing {h5path}", flush=True)

    print(f"[{time.strftime('%H:%M:%S')}] opening h5ad ...", flush=True)
    h = h5py.File(h5path, "r")
    gn = [x.decode() if isinstance(x, bytes) else x for x in h['var']['gene_name'][:]]
    gni = {g: i for i, g in enumerate(gn)}
    present = [g for g in PANEL if g in gni]
    missing = [g for g in PANEL if g not in gni]
    cols = [gni[g] for g in present]
    print(f"  present {len(present)} / {len(PANEL)}; missing: {missing}", flush=True)

    # h5py fancy-indexing needs increasing column order, then reorder back to `present`
    order = np.argsort(cols)
    sorted_cols = list(np.array(cols)[order])
    back = np.argsort(order)

    print(f"[{time.strftime('%H:%M:%S')}] slicing log_fc ...", flush=True)
    lfc = h['layers']['log_fc'][:, sorted_cols][:, back].astype(np.float32)
    print(f"[{time.strftime('%H:%M:%S')}] slicing zscore ...", flush=True)
    z = h['layers']['zscore'][:, sorted_cols][:, back].astype(np.float32)

    meta = pd.DataFrame({
        'target': read_obs(h, 'target_contrast_gene_name').astype(str),
        'condition': read_obs(h, 'culture_condition').astype(str),
        'n_cells': np.asarray(read_obs(h, 'n_cells_target'), float),
        'ontarget_sig': read_obs(h, 'ontarget_significant').astype(str),
        'ontarget_es': np.asarray(read_obs(h, 'ontarget_effect_size'), float),
    })

    npz = os.path.join(args.outdir, "ko_receptor_DE.npz")
    pq = os.path.join(args.outdir, "ko_receptor_DE_meta.parquet")
    np.savez_compressed(npz, lfc=lfc, z=z, genes=np.array(present))
    meta.to_parquet(pq)
    print(f"[{time.strftime('%H:%M:%S')}] wrote {npz} ({os.path.getsize(npz)/1e6:.1f} MB) and {pq}", flush=True)
    print(f"  lfc {lfc.shape}  z {z.shape}  meta {meta.shape}", flush=True)

    if h5path == os.path.join(args.outdir, "GWCD4i.DE_stats.h5ad") and not args.keep_h5:
        os.remove(h5path)
        print(f"  removed {h5path}", flush=True)

    with open(os.path.join(args.outdir, "extract_DONE.json"), "w") as f:
        json.dump({"present": present, "missing": missing,
                   "npz_mb": os.path.getsize(npz)/1e6, "rows": int(meta.shape[0])}, f, indent=2)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
