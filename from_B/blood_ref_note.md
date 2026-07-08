# Blood-reference arm — results for A (Session B)

**Session B frame_id:** `4e3cb286-81d6-4f72-8a87-bd5c067c0499`
**Cohort:** Guo 2018 NSCLC, GEO **GSE99254** (Smart-seq2, raw counts `S12346.count`).
This is one of the three cohorts Zheng integrated, and it has the cleanest paired
design of the candidates: **14 patients, all with paired blood + tumor**; 12 with
full P/N/T triads. Location and CD4 sub-gate are both encoded in the cell barcode
(`P/N/T` = blood/adj-normal/tumor; FACS gate `H` = CD4 conventional, `R` = Treg,
`C` = CD8). The R gate is transcriptomically confirmed Treg (FOXP3 / IL2RA / CTLA4 /
IKZF2-hi), so Arm A/Arm B separation is authoritative, not inferred.

## Method (matches the recipe exactly)
33-gene panel, fixed order; CD4 only; pseudobulk = sum raw counts per
(patient × subset × loc); CLR = (counts+0.5) → proportions over 33 → log → minus
per-profile mean; within-subset paired **Δ = CLR(T) − CLR(P)** (blood→tumor) for
each (patient × subset) with ≥20 cells on **both** sides; Wilcoxon signed-rank per
gene; BH-FDR over 33 genes.
Subsets: `CD4conv_naive` (CCR7/SELL/TCF7-hi), `CD4conv_mem` (GZMK/GZMB/CXCR3-hi),
`Treg` (= R gate). **Arm A** = the two conventional subsets (Treg excluded); **Arm B**
= Treg only.

## Deliverable for `match_engine.py`
**`blood_ref_delta_within_subset.parquet`** — DataFrame indexed by the 33 panel genes
**in the required order**, columns `delta, frac_up, p, fdr`. Drop the `delta` column
in as your target vector. **n = 10 paired (patient × subset)** observations, Treg
excluded.

## Headline: the egress artifact you flagged is resolved — reference-dependent
Against a **true circulating reference**, the egress/recirculation receptors do not
show the "gained in tumor" signal they showed against your adjacent-normal reference.
Two of them (**SELL, S1PR1**) actually **flip sign** — positive vs normal, negative
vs blood — and the rest either shrink toward zero (**CCR7**) or go more strongly
negative (**S1PR4, S1PR5, CX3CR1**):

| receptor | Δ vs **blood** (T−P) | Δ vs **normal** (T−N) | behaviour |
|---|---|---|---|
| S1PR1 | **−0.84** (p=0.027) | +0.49 | **flips** (+→−) |
| SELL  | **−0.32** | +1.53 | **flips** (+→−) |
| CCR7  | +0.46 | +1.68 | shrinks, stays + |
| S1PR4 | −0.64 (p=0.037) | −0.32 | more negative |
| S1PR5 | −1.58 | −0.84 | more negative |
| CX3CR1| −2.87 (FDR 0.032) | −1.32 | more negative |

So your "egress/recirculation UP in tumor" signal was largely a **property of the
adjacent-normal reference** (those CD4s are terminally tissue-resident, egress fully
off), **not** tumor CD4s recirculating. The clearest evidence is SELL and S1PR1
reversing direction with the reference change; CCR7 stays weakly positive vs blood
(+0.46) so it is only attenuated, not reversed. With blood as the baseline the
egress receptors as a group are flat-to-down, so the target direction should be built
on the blood reference, and the normal-referenced egress-up signal should not be
interpreted as "cells leaving the tumor."

## Arm A (conventional CD4, Treg excluded), blood→tumor
FDR<0.1 genes: **CCR6** (Δ+1.24, FDR 0.032, 10/10 pairs up), **CXCR5** (Δ+1.84,
FDR 0.064), **CX3CR1** (Δ−2.87, FDR 0.032, 0/10 up).
Top gains: CXCR5, CCR4, CCR8, CCR1, CXCR6 (inflammatory / B-follicle / Th2-Treg homing).
Top losses: CCR10, CX3CR1, S1PR5, ACKR4, ACKR3 (egress + atypical/scavenger receptors).

## Arm B (Treg only), blood→tumor — `blood_ref_delta_treg.parquet`
n = 8 paired patients. Tumor Tregs gain inflammatory-homing + tissue-residency
receptors from blood: **CXCR6** (Δ+2.90, FDR 0.064), **CCR5** (+1.83, FDR 0.064),
**CXCR3** (+1.28, FDR 0.064), **CCR8** (+2.02, FDR 0.074), **ITGAE** (+0.90, FDR 0.074);
and lose egress/gut receptors: **S1PR1** (−1.99), **CCR10** (−3.89), **GPR15** (−3.29).

## CCR8 verdict (your specific question)
Against a real blood reference, **CCR8 is a genuine blood→tumor gain, not merely a
Treg-identity marker**:
- Treg (T−blood): **Δ+2.02, p=0.016**
- conv CD4 (T−blood): Δ+1.58 (p=0.084)
- conv CD4 (T−normal): **Δ−0.74, ns** ← your adjacent-normal reference masks it,
  because adjacent-normal tissue CD4s already express CCR8.

So CCR8 rises from blood into tumor in **both** Treg and conventional CD4; it's not
purely a suppressive-identity artifact. It was invisible in the normal→tumor contrast
only because the reference tissue is already CCR8-high. (Your finding that CCR8 is a
Treg-*identity* marker still holds — it's just *also* a real tumor-entry gain.)

## Files (relayed via the user)
- `blood_ref_delta_within_subset.parquet` — **PRIMARY target for match_engine** (Arm A, 33 genes × {delta,frac_up,p,fdr})
- `blood_ref_delta_perpair.parquet` — per-(patient×subset) Δ matrix (10 × 33), Arm A
- `blood_ref_delta_treg.parquet` — Arm B (Treg) target
- `blood_ref_delta_vs_normal.parquet` — T−N conv cross-check (for the polarity comparison above)
- `fig_blood_ref_delta.png` — diagnostic figure

## Caveats
- Smart-seq2 plate data (deep, ~3000 genes/cell, no MT genes in matrix); n on the
  smaller side (10 conv pairs / 8 Treg pairs) — FDR<0.1 used as the significance
  gate. `delta` and `frac_up` are the robust signals; treat individual p-values as
  directional support, not confirmatory.
- Subsets are Leiden-derived functional groups within the CD4 FACS gates. The Treg
  subset equals the R gate exactly (100% concordant), so Arm A/Arm B are clean.
