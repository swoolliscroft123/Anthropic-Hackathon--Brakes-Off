"""
match_engine.py — Session A · shared matching machinery for the brake-nomination pipeline.

Scores each Perturb-seq knockout's receptor-space shift (Δ_KO) against a target
direction (Δ_target) — e.g. the retention/egress vector (Arm A) or the anti-Treg
vector (Arm B). Target-agnostic: pass any 33-dim Δ vector on the receptor panel.

Conventions (must match SYNC_BRIEF §6):
  - genes: the 33-gene receptor panel, fixed order.
  - Δ vectors live in CLR (Aitchison) space; a Δ is already a difference of CLRs,
    so it is mean-zero-ish across the panel and directly comparable by cosine.
  - hold_out: if the KO'd gene is in the panel, zero BOTH vectors on that gene
    before scoring (anti-circularity, SYNC_BRIEF §6.6).
"""
import numpy as np, pandas as pd

def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v

def score_ko(delta_ko, delta_target, hold_out_gene=None, genes=None):
    """One KO vs target. Returns cosine, signed projection, and gained/lost split."""
    dko = np.asarray(delta_ko, float).copy()
    dtg = np.asarray(delta_target, float).copy()
    if hold_out_gene is not None and genes is not None and hold_out_gene in list(genes):
        j = list(genes).index(hold_out_gene)
        dko[j] = 0.0; dtg[j] = 0.0
    cos = float(np.dot(_unit(dko), _unit(dtg)))
    proj = float(np.dot(dko, _unit(dtg)))            # magnitude of Δ_KO along target
    # decompose: of the alignment, how much is "moves the right genes up" vs "down"
    aligned = dko * dtg                               # >0 where KO agrees with target sign
    gained = float(aligned[(dtg > 0)].sum())          # target-up genes the KO pushes up
    lost   = float(aligned[(dtg < 0)].sum())          # target-down genes the KO pushes down
    return dict(cosine=cos, projection=proj, align_gained=gained, align_lost=lost)

def score_matrix(DKO, delta_target, genes, hold_out=True, n_perm=2000, seed=0):
    """
    DKO: DataFrame (KO x genes) of Δ_KO vectors. delta_target: Series indexed by genes.
    Permutation null: shuffle gene labels of the TARGET n_perm times, recompute cosine,
    empirical two-sided p per KO. Returns a ranked DataFrame.
    """
    genes = list(genes)
    tgt = delta_target.reindex(genes).values.astype(float)
    rng = np.random.default_rng(seed)
    rows = []
    for ko, row in DKO.iterrows():
        ho = ko if (hold_out and ko in genes) else None
        s = score_ko(row.values, tgt, hold_out_gene=ho, genes=genes)
        s["knockout"] = ko
        rows.append(s)
    R = pd.DataFrame(rows).set_index("knockout")
    # permutation null on cosine (label-shuffle the target; KO vectors fixed)
    obs = R["cosine"].values
    null_ge = np.zeros(len(R))
    Dk = DKO.reindex(columns=genes).values.astype(float)
    Dk_u = Dk / (np.linalg.norm(Dk, axis=1, keepdims=True) + 1e-12)
    for _ in range(n_perm):
        pt = _unit(rng.permutation(tgt))
        null_cos = Dk_u @ pt
        null_ge += (np.abs(null_cos) >= np.abs(obs)).astype(float)
    R["p_perm"] = (null_ge + 1) / (n_perm + 1)
    from statsmodels.stats.multitest import multipletests
    R["fdr"] = multipletests(R["p_perm"], method="fdr_bh")[1]
    return R.sort_values("cosine", ascending=False)

if __name__ == "__main__":
    # ---- unit test on synthetic data: a planted "perfect brake" must top the ranking ----
    genes = [f"g{i}" for i in range(33)]
    rng = np.random.default_rng(1)
    target = pd.Series(rng.normal(size=33), index=genes)
    # 200 random KOs + 3 planted: exact match, anti-match, and noise
    D = pd.DataFrame(rng.normal(scale=0.3, size=(200, 33)),
                     index=[f"KO{i}" for i in range(200)], columns=genes)
    D.loc["PERFECT"] = target.values * 1.5
    D.loc["ANTI"] = -target.values * 1.5
    D.loc["g5"] = target.values.copy(); D.loc["g5", "g5"] = 10.0   # circularity trap on g5
    R = score_matrix(D, target, genes, hold_out=True, n_perm=1000)
    top = R.index[0]; anti_rank = R.index.get_loc("ANTI")
    print("top KO:", top, "(expect PERFECT)")
    print("PERFECT cosine:", round(R.loc["PERFECT","cosine"],3), "fdr:", round(R.loc["PERFECT","fdr"],4))
    print("ANTI cosine:", round(R.loc["ANTI","cosine"],3), "rank:", anti_rank, "of", len(R), "(expect last)")
    print("g5 held-out cosine:", round(R.loc["g5","cosine"],3),
          "(circularity gene zeroed; should be high but not from g5)")
    assert top == "PERFECT", "planted perfect match must rank #1"
    assert anti_rank >= len(R)-2, "anti-match must rank near bottom"
    print("UNIT TEST PASSED")
