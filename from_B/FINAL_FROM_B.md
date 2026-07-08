# FINAL HANDOFF — Session B → A (coordination wind-down)

The user is closing the two-session back-and-forth. This is B's single consolidated
handoff: everything B produced, everything B learned, and exactly what A needs to
finish the project solo. No further B round-trips assumed — treat B's deliverables in
`from_B/` as final unless a bug surfaces.

B frame_id: `4e3cb286-81d6-4f72-8a87-bd5c067c0499` (proj_4133815719e1).

---

## 1. What B delivered (all in `from_B/`, validated by A)

**Blood-reference target arm — DONE.** Cohort: Guo 2018 NSCLC (GSE99254), 14 patients
all paired blood+tumor (12 P/N/T triads), Smart-seq2, FACS gates giving an
authoritative conv/Treg split (R gate = 100% concordant with transcriptomic Treg).

| file | role |
|---|---|
| `blood_ref_delta_within_subset.parquet` | **PRIMARY engine target** — Arm A conv-CD4 blood→tumor Δ, 33 genes × {delta,frac_up,p,fdr}, panel order. Drop `delta` in as the target vector. n=10 (patient×subset). |
| `blood_ref_delta_perpair.parquet` | per-pair Δ matrix, 10×33 |
| `blood_ref_delta_treg.parquet` | Arm B (Treg) target, n=8 |
| `blood_ref_delta_vs_normal.parquet` | T−N cross-check (the reference-flip comparison) |
| `blood_ref_note.md` | full methods + results note |
| `fig_blood_ref_delta.png`, `fig_cd4_qc_markers.png`, `fig_cd4_umap_subsets.png` | figures |

**Core findings (objective, TIL = tumor-infiltrating CD4):**
- **Treg confound (corroborated by A's atlas):** the naïve top "homing" signal is Treg
  compartment expansion, not receptor rewiring.
- **Reference flips egress polarity (replicated across both datasets):** vs
  adjacent-normal, egress receptors look gained in tumor; vs true blood, **S1PR1
  (+0.49→−0.84) and SELL (+1.53→−0.32) flip sign**. CCR7 does NOT flip (stays weakly +,
  +0.47 vs blood). **S1PR4/S1PR5/CX3CR1 are DOWN under BOTH references — not flips**
  (this correction confirmed on both sides; A caught it independently).
- **Blood-referenced signature:** egress DOWN (CX3CR1 −2.87 FDR 0.032, 0/10 up; S1PR1
  −0.84), tissue-entry UP (CCR6 +1.24 FDR 0.032, 10/10 up; CXCR5 +1.84; CXCR6/CCR4/CXCR4).
- **CCR8:** genuine blood→tumor gain (Treg +2.02 p=0.016; conv +1.58), invisible vs
  adjacent-normal (−0.74 ns) because normal tissue is already CCR8-high.

## 2. KO-matrix ingest — TOOLING READY, needs a human run on BMRC

The genome-scale Perturb-seq DE matrix (GWCD4i.DE_stats.h5ad, 16.8 GB) is NOT yet
ingested — this is the one remaining blocker to any KO ranking. B's sandbox is
proxy-throttled (~0.43 MB/s/conn); the decision (user + A) is to run it on **BMRC**.

**Ready in `from_B/bmrc_scripts/`** (tested locally on a synthetic h5ad — column-order,
value-correctness, full-archive losslessness all verified):
- `extract_ko_receptors.py` — **dual output** from one download:
  1. SLIM (git-relayable, ~10 MB): `ko_receptor_DE.npz` (keys lfc, z, padj, genes=25
     present receptors in panel order) + `ko_receptor_DE_meta.parquet` (target,
     condition, n_cells, ontarget_sig, ontarget_es, offtarget).
  2. FULL-GENE ARCHIVE (~5-6 GB, stays on scratch / pull as needed): `ko_full_DE.h5`
     — all 10,282 genes × all 6 layers (log_fc, zscore, adj_p_value, baseMean, lfcSE,
     p_value), float32, gzip-chunked, + full obs + var. **This is the broad net** so
     we're not receptor-locked (see §3 — we need P2RY8/GNA13/etc, not just receptors).
- `submit_bmrc.sh` (SLURM), `1_run_on_bmrc.sh` / `2_check_bmrc.sh` / `3_fetch_from_bmrc.sh`
  (fire-and-forget; user runs from their PC where BMRC SSH/2FA works).

**Whoever finishes this:** run the 3 scripts, drop `ko_receptor_DE.npz` +
`_meta.parquet` in `from_B/`, keep `ko_full_DE.h5` on scratch. Then A runs the engine.

## 3. The reframe that changes the project (READ — from B's paper review)

The user flagged a possible scoop: Liu, Carnevale et al. (UCSF), bioRxiv
10.1101/2025.09.23.678127 — in-vivo genome-wide CRISPR screens in human T cells.
(A. Marson is a senior co-author; corresponding authors are Liu & Carnevale.)

**B read it end-to-end. The lane is OPEN and the paper is our validation anchor:**
- They did NOT do Perturb-seq, patient-TIL analysis, single-cell, receptor repertoire,
  or compositional/CLR matching. Their method is a phenotypic abundance/IFN-γ screen in
  *mouse-resident healthy-donor* human T cells + GO-GSEA. Zero overlap with our pipeline.
- They explicitly name BOTH halves of our approach (Perturb-seq linkage; patient-TIL
  screening) as *future work* in their Discussion.
- **Convergence = the win:** their infiltration hits are the P2RY8–Gα13 GPCR pathway
  (P2RY8, GNA13, ARHGEF1, S1PR1, CXCR4, PTGER4), mechanism = the S1PR1 egress/retention
  axis. That's our blood-referenced egress-DOWN result from the opposite direction. Two
  orthogonal assays, two systems, one axis.

**Project reframes** from "discover a novel gene" (dead — they're first) to **"a
patient-anchored compositional method that recovers in-vivo-validated GPCR-trafficking
brakes AND extends them with receptor-rewiring hits."** Stronger, because it now has an
external answer key. Full detail: `from_B/from_B_CONCORDANCE_BRIEF.md`.

## 4. A's to-do list (solo, in priority order)

1. **When the KO matrix lands:** CLR-center it in receptor space, run `match_engine.py`
   against B's `blood_ref_delta_within_subset.parquet` (Arm A) and `blood_ref_delta_treg.parquet`
   (Arm B). Produce `ko_ranking.csv` + the payoff figure (top KOs' Δ_KO projected on the
   target direction).
2. **Concordance test (pre-registered):** report where the answer-key genes
   `P2RY8, GNA13, ARHGEF1, S1PR1, CXCR4, PTGER4` rank (rank + percentile + a rank-based
   enrichment p). High concordance ⇒ method validated. Top-ranked KOs NOT in their
   screen ⇒ candidate novel receptor-rewiring hits. Only genes in the 10,282 var can be
   scored — verify P2RY8/GNA13 are present in the real matrix (they were in B's schema test).
3. **Open flag from A's own spot-audit:** full 33-vector agreement between A's
   normal-referenced atlas target and B's blood target is weak (Spearman ρ=−0.04, 48%
   sign agreement) — egress axis agrees, full vectors don't. Tangles cancer type
   (pan-cancer vs NSCLC) + subset granularity (24 clusters vs 3 gates) + platform (10X
   vs SS2). **Must be resolved before candidate calls.** B proposed the clean separator:
   re-run B's Δ at finer subset granularity, re-report ρ (rise ⇒ nuisance; flat ⇒
   cancer-type biology). If B doesn't get to it, A can do the same test from the atlas side.
4. **Replication cohort (priority raised by A):** run B's exact blood-reference recipe on
   GSE108989 (CRC) or GSE98638 (HCC) via BMRC → `blood_ref_delta_within_subset_REP.parquet`.
   Tests whether the KO-matching target is cancer-type-stable or NSCLC-idiosyncratic.

## 5. Logistics / gotchas
- **Relay:** GitHub repo `swoolliscroft123/Anthropic-Hackathon--Brakes-Off` (branch main)
  is the source of truth; also mirrored to `~/Desktop/Anthropic hackathon project/from_B/`.
- **BMRC:** automated SSH from the sandbox is NOT authorized (probe fails on publickey);
  the user runs BMRC scripts interactively from their PC. Route heavy compute there.
- **GSE99254 quirks:** no MT genes in the matrix (Guo removed them); 3 cell-name format
  variants; R FACS gate = Treg. Details in `blood_ref_note.md`.
- **Numba/sandbox:** scanpy needs `numba.config.DISABLE_JIT=True` at import; UMAP needs
  JIT back ON (10s vs 335s). Only relevant if re-running B's clustering.

— B, signing off on active coordination.
