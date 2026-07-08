#!/usr/bin/env python3
"""
Ingest the Marson 2025 genome-scale Perturb-seq DE matrix
(GWCD4i.DE_stats.h5ad, 16.8 GB) on BMRC, where the S3 bucket is reachable at
full speed. Casts a BROAD net: from the single download it produces TWO products.

Outputs (written to --outdir):
  1. SLIM (for Session A via git; ~10 MB):
       ko_receptor_DE.npz          : lfc, z, padj (each 33983x25 f32), genes (25,)
       ko_receptor_DE_meta.parquet : obs (target, condition, n_cells,
                                      ontarget_sig, ontarget_es, offtarget)
  2. FULL-GENE ARCHIVE (reusable; ~5-6 GB, stays on scratch / pull as needed):
       ko_full_DE.h5               : all 10,282 genes x all 6 layers, float32,
                                      + full obs table + var (gene_name, gene_ids).
                                      Layers: log_fc, zscore, adj_p_value,
                                      baseMean, lfcSE, p_value. gzip-compressed,
                                      chunked by row-block for partial reads.

Reopen the full archive later with h5py:
    f = h5py.File("ko_full_DE.h5"); f["layers/log_fc"][:, gene_idx]
    obs = pd.read_hdf("ko_full_DE.h5", "obs")   # if written via pandas; here obs is
                                                 # a group — see read helper in repo.

Run on a BMRC compute node (see submit_bmrc.sh). Needs: numpy, pandas, h5py, pyarrow.
Memory: opens one 2.8 GB float64 layer at a time and writes it out as float32,
so peak RSS stays ~3-4 GB; --mem=64G is comfortable headroom.
"""
import os, sys, json, time, argparse
import numpy as np, pandas as pd, h5py

ALL_LAYERS = ["log_fc", "zscore", "adj_p_value", "baseMean", "lfcSE", "p_value"]
ALL_OBS = ["target_contrast_gene_name", "culture_condition", "n_cells_target",
           "ontarget_significant", "ontarget_effect_size", "distal_offtarget_flag",
           "target_baseMean", "ontarget_significant", "n_up_genes", "n_down_genes",
           "n_total_de_genes", "n_guides", "guide_correlation_signif", "chunk"]

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

def build_meta(h):
    """Full obs table (all fields that exist), plus the named essentials."""
    cols = {}
    # essential renamed fields for the slim product
    ren = {'target_contrast_gene_name': 'target', 'culture_condition': 'condition',
           'n_cells_target': 'n_cells', 'ontarget_significant': 'ontarget_sig',
           'ontarget_effect_size': 'ontarget_es', 'distal_offtarget_flag': 'offtarget'}
    for raw, nice in ren.items():
        if raw in h['obs']:
            cols[nice] = read_obs(h, raw)
    # plus every remaining obs field, under its own name (broad net)
    for name in h['obs']:
        if name in ('__categories',):  # skip anndata internals
            continue
        if name in ren:
            continue
        try:
            cols[name] = read_obs(h, name)
        except Exception as e:
            print(f"  (skipped obs/{name}: {e})", flush=True)
    return pd.DataFrame(cols)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--h5", default=None,
                    help="Path to a local GWCD4i.DE_stats.h5ad. If omitted, downloads from S3 to --outdir.")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--full-out", default=None,
                    help="Path for the full-gene float32 archive (default: <outdir>/ko_full_DE.h5). "
                         "Put this on scratch — it's ~5-6 GB.")
    ap.add_argument("--no-full", action="store_true",
                    help="Skip the full-gene archive; produce only the slim receptor product.")
    ap.add_argument("--keep-h5", action="store_true", help="Keep the downloaded 16.8 GB h5ad.")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    h5path = args.h5
    if h5path is None:
        h5path = os.path.join(args.outdir, "GWCD4i.DE_stats.h5ad")
        if not os.path.exists(h5path):
            print(f"[{time.strftime('%H:%M:%S')}] downloading 16.8 GB h5ad from S3 ...", flush=True)
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
    nrows, ncol = h['layers']['log_fc'].shape
    print(f"  matrix {nrows}x{ncol}; panel present {len(present)}/{len(PANEL)}; missing: {missing}", flush=True)

    # h5py fancy-indexing needs increasing column order, then reorder back to `present`
    order = np.argsort(cols); sorted_cols = list(np.array(cols)[order]); back = np.argsort(order)

    meta = build_meta(h)
    print(f"  obs table: {meta.shape[1]} fields x {meta.shape[0]} rows", flush=True)

    # ---- FULL-GENE ARCHIVE: stream each layer float64->float32 to a chunked, gzipped h5 ----
    full_out = args.full_out or os.path.join(args.outdir, "ko_full_DE.h5")
    slim = {}   # panel-sliced layers reused from the full pass, no re-read
    if not args.no_full:
        print(f"[{time.strftime('%H:%M:%S')}] writing full-gene float32 archive -> {full_out}", flush=True)
        BLK = 4000  # rows per write block; ~160 MB/block float32
        with h5py.File(full_out, "w") as fo:
            lg = fo.create_group("layers")
            for lyr in ALL_LAYERS:
                if lyr not in h['layers']:
                    print(f"  (layer {lyr} absent, skipping)", flush=True); continue
                src = h['layers'][lyr]
                dset = lg.create_dataset(lyr, shape=(nrows, ncol), dtype='float32',
                                         chunks=(min(BLK, nrows), ncol),
                                         compression='gzip', compression_opts=4)
                acc = []  # collect panel columns for the slim product as we stream
                for r0 in range(0, nrows, BLK):
                    r1 = min(r0 + BLK, nrows)
                    block = src[r0:r1, :].astype(np.float32)   # read float64 block, cast
                    dset[r0:r1, :] = block
                    if lyr in ('log_fc', 'zscore', 'adj_p_value'):
                        acc.append(block[:, sorted_cols][:, back])
                if acc:
                    slim[lyr] = np.concatenate(acc, axis=0)
                print(f"    {lyr} done", flush=True)
            # var + obs into the archive
            vg = fo.create_group("var")
            vg.create_dataset("gene_name", data=np.array(gn, dtype='S32'))
            if 'gene_ids' in h['var']:
                gids = [x.decode() if isinstance(x, bytes) else x for x in h['var']['gene_ids'][:]]
                vg.create_dataset("gene_ids", data=np.array(gids, dtype='S32'))
            og = fo.create_group("obs")
            for c in meta.columns:
                og.create_dataset(c, data=meta[c].astype(str).values.astype('S64'))
        print(f"  full archive {os.path.getsize(full_out)/1e9:.2f} GB", flush=True)
    else:
        # no full pass: slice the 3 DE layers directly for the slim product
        for lyr in ('log_fc', 'zscore', 'adj_p_value'):
            slim[lyr] = h['layers'][lyr][:, sorted_cols][:, back].astype(np.float32)

    # ---- SLIM RECEPTOR PRODUCT (for A, git-relayable) ----
    lfc, z, padj = slim['log_fc'], slim['zscore'], slim['adj_p_value']
    npz = os.path.join(args.outdir, "ko_receptor_DE.npz")
    pq = os.path.join(args.outdir, "ko_receptor_DE_meta.parquet")
    np.savez_compressed(npz, lfc=lfc, z=z, padj=padj, genes=np.array(present))
    # slim meta = just the named essentials, in a stable column order
    slim_cols = [c for c in ['target','condition','n_cells','ontarget_sig','ontarget_es','offtarget'] if c in meta]
    meta[slim_cols].to_parquet(pq)
    print(f"[{time.strftime('%H:%M:%S')}] wrote {npz} ({os.path.getsize(npz)/1e6:.1f} MB) and {pq}", flush=True)
    print(f"  lfc {lfc.shape}  z {z.shape}  padj {padj.shape}  meta {meta[slim_cols].shape}", flush=True)

    if h5path == os.path.join(args.outdir, "GWCD4i.DE_stats.h5ad") and not args.keep_h5:
        os.remove(h5path)
        print(f"  removed raw {h5path}", flush=True)

    with open(os.path.join(args.outdir, "extract_DONE.json"), "w") as f:
        json.dump({"present": present, "missing": missing,
                   "npz_mb": round(os.path.getsize(npz)/1e6, 1),
                   "full_archive": (None if args.no_full else full_out),
                   "full_gb": (None if args.no_full else round(os.path.getsize(full_out)/1e9, 2)),
                   "rows": int(meta.shape[0]), "genes": int(ncol),
                   "obs_fields": list(meta.columns)}, f, indent=2)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
