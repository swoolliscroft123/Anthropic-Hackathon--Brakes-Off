# PROJECT STATE — "Brakes Off": nominating druggable brakes on CD4 tumor infiltration
*Joint A + B synthesis · compiled by Session B, for review by A · 2026-07-08*

## The one-sentence project
Mine genome-scale CRISPR Perturb-seq in human CD4⁺ T cells for gene knockouts that
reshape a T cell's chemokine/homing-receptor repertoire toward the state real
tumor-infiltrating CD4s adopt — matched in **receptor space** on **compositional
(CLR) fingerprints**. A KO that reproduces the tumor-entry/retention receptor shift is
a candidate **brake** whose inhibition could improve infiltration.

The pipeline has two arms that meet at a matching engine:
- **Target arm (Δ_tumor):** where do real TIL CD4s sit in receptor space vs a reference?
- **Perturbation arm (Δ_KO):** how does each knockout move CD4 receptor space?
- **Engine:** score every KO's Δ_KO against the target Δ (cosine + signed projection,
  permutation null, KO'd-gene hold-out). Target-agnostic, unit-tested.

---

## 1. What we have SHOWN (objective statements)

Each statement is tagged with the evidence and the figure that shows it. "TIL" =
tumor-infiltrating CD4 T cell.

### About the receptor repertoire of tumor-infiltrating CD4s

**S1. The naïve top hit — CCR8 "homing" — is a Treg-composition artifact.**
On tumor infiltration Tregs rise from 14%→35% of the CD4 compartment, and **90% of
CCR8⁺ tumor CD4s are Tregs**. The unadjusted #1 "tumor-homing" receptor signal is
therefore *which cells are present* (suppressive compartment expanding), not
*anti-tumor cells rewiring their receptors*. → **Fig treg_confound.png** (A, atlas).

**S2. Reference choice determines the entire polarity of the egress signal.**
The same TILs compared against two references give opposite conclusions for the
lymph-node-egress/recirculation receptors:

| receptor | Δ vs adjacent-normal (A) | Δ vs true blood (B) | verdict |
|---|---|---|---|
| S1PR1 | **+0.50** (up) | **−0.84** (down, p=0.027) | **sign flip** |
| SELL  | **+1.53** (up) | **−0.32** (down) | **sign flip** |
| CCR7  | +1.69 (up) | +0.47 (weakly up) | attenuates, no flip |
| S1PR4 | −0.32 | −0.64 (p=0.037) | consistent down |
| CX3CR1| −1.32 | −2.87 (FDR 0.032) | consistent down |

Against adjacent-normal tissue (whose CD4s are terminally resident, egress fully off)
egress receptors *look* gained in tumor; against circulating blood they are flat-to-
**lost**. The adjacent-normal "egress-up" signal was a **residency floor of the
reference**, not TILs recirculating. → **Fig fig_blood_ref_delta.png panel B** (B).

**S3. With a true circulating reference, TIL CD4s show the expected retention/entry
polarity.** Blood→tumor within-subset (Treg-excluded, n=10 patient×subset pairs):
- **Egress machinery DOWN:** CX3CR1 (Δ−2.87, FDR 0.032, 0/10 pairs up), S1PR1
  (−0.84, p=0.027), S1PR4 (−0.64, p=0.037), S1PR5 (−1.58).
- **Tissue-homing / inflammatory receptors UP:** CCR6 (Δ+1.24, FDR 0.032, **10/10
  pairs up**), CXCR5 (+1.84, FDR 0.064), CXCR6 (+1.35), CCR4 (+1.84), CXCR4 (+0.82,
  p=0.049), CCR8 (+1.58).
This is the coherent "downregulate the machinery for leaving tissue, upregulate the
machinery for entering/being retained in inflamed tissue" signature. → **Fig
fig_blood_ref_delta.png panel A** (B).

**S4. CCR8 IS a genuine blood→tumor gain — but only visible against blood.**
- within-Treg, blood→tumor: **Δ+2.02, p=0.016** (real gain on tumor entry)
- within-conv CD4, blood→tumor: Δ+1.58
- within-conv CD4, vs adjacent-normal: **Δ−0.74, n.s.** (invisible)
- within-Treg, vs adjacent-normal (A): rank 10, n.s. (Δ0.25)
CCR8 marks Treg *identity* (S1) **and** rises from blood into tumor in both Treg and
conventional CD4 (S4). The adjacent-normal reference masked the entry-gain because
normal-tissue CD4s are already CCR8-high. → **Fig fig_blood_ref_delta.png panel C** (B).

**S5. The blood-referenced target direction is compartment-specific.** In the Treg
arm (Arm B, blood→tumor, n=8) tumor Tregs gain a distinct inflammatory/residency set
— CXCR6 (Δ+2.90, FDR 0.064), CCR5 (+1.83, FDR 0.064), CXCR3 (+1.28, FDR 0.064), CCR8
(+2.02), ITGAE (+0.90) — and lose egress/gut receptors (S1PR1 −1.99, CCR10 −3.89,
GPR15 −3.29). Unlike the adjacent-normal reference (which gave A a
compartment-*nonspecific* tissue-adaptation axis in both arms), the blood reference
separates a conventional-CD4 target from a Treg target.

### Methodological statement
**S6. The confound cascade is why the reference mattered.** Naïve homing signal →
Treg composition (S1) → after Treg exclusion + within-subset control, only egress
survived (A) → but egress was entangled with the residency floor of adjacent-normal
(S2) → a true blood reference resolves it (S3). The project's central methodological
result is that **the target direction is only interpretable against a circulating
reference**; adjacent-normal tissue is not a valid baseline for "infiltration."

---

## 2. Deliverables so far

### Session B (blood-reference arm) — DONE, validated by A
| file | what it is |
|---|---|
| `blood_ref_delta_within_subset.parquet` | **PRIMARY target** for the engine: Arm A conv-CD4 blood→tumor Δ, 33 genes × {delta,frac_up,p,fdr} |
| `blood_ref_delta_perpair.parquet` | per-(patient×subset) Δ matrix, 10×33 |
| `blood_ref_delta_treg.parquet` | Arm B (Treg) blood→tumor target, 8 pairs |
| `blood_ref_delta_vs_normal.parquet` | T−N cross-check (the S2 comparison) |
| `fig_blood_ref_delta.png` | 3-panel: ranked Δ + reference-flip + CCR8 |
| `fig_cd4_qc_markers.png` | QC + FACS-gate validation |
| `fig_cd4_umap_subsets.png` | CD4 subset annotation |
| `blood_ref_note.md` | full handoff note |
Cohort: **Guo 2018 NSCLC (GSE99254)**, 14 patients all paired blood+tumor (12 P/N/T
triads), Smart-seq2. FACS gates give an authoritative conv/Treg split (R gate = 100%
concordant with transcriptomic Treg).

### Session A (target arm + engine) — DONE
| file | what it is |
|---|---|
| `match_engine.py` | target-agnostic KO↔target scorer; unit-tested (planted match ranks #1) |
| `atlas_delta_tumor*.parquet` + `delta_tumor_within_subset.parquet` | atlas (GSE156728) adjacent-normal→tumor target, 5 cancers, 58,892 CD4 |
| `armB_treg_target_within_subset.parquet` | atlas within-Treg target |
| `treg_confound.png` | the S1 figure |
| `delta_tumor_target_direction.png` | atlas target direction |
| `receptor_panel_v1.json`, `cd4_compartment_map.json`, `pipeline_design.md` | shared coordinate system |

### NOT YET DONE (the open critical path)
- **KO ingest / ranking.** The genome-scale Perturb-seq DE matrix (Marson 2025,
  16.8 GB) is not yet sliced to receptor space, so **no KO has been scored against any
  target yet.** This is the one thing standing between us and the project's actual
  output (a ranked brake list). B is fetching it (sandbox, throttled) with a BMRC
  fallback (scripts written).
- **Replication cohort** (GSE108989 CRC / GSE98638 HCC) — optional robustness, not started.

---

## 3. The figures that prove it elegantly

Ranked by how cleanly each carries a claim:

1. **fig_blood_ref_delta.png panel B (reference-flip scatter)** — the single most
   important figure. Δ-vs-normal on x, Δ-vs-blood on y; egress receptors highlighted;
   the shaded quadrant is "gained vs normal, lost vs blood." SELL and S1PR1 sit in it.
   One glance shows the entire project's methodological pivot (S2, S6).
2. **treg_confound.png** (A) — shows S1: the naïve top hit is compartment composition.
   This is the "why the obvious answer is wrong" figure; it motivates everything.
3. **fig_blood_ref_delta.png panel A (ranked Δ lollipop)** — shows S3: egress down,
   homing up, with FDR rings and egress receptors color-threaded. The clean
   directional result.
4. **fig_blood_ref_delta.png panel C (CCR8 across contrasts)** — shows S4 in three
   bars: CCR8 gained vs blood (Treg p=0.016), invisible vs normal. Resolves A's
   specific CCR8 question in one panel.

**Figure gap for the final story (proposed, needs the KO data):** a **KO-ranking
figure** — the target direction (down-egress / up-homing) with the top-ranked
knockouts' Δ_KO projected onto it, showing which brakes reproduce the TIL shift. This
is the payoff panel and doesn't exist yet because the KO matrix isn't ingested.

---

## 4. What each session should do next (proposed — for A to confirm)
- **B:** finish the KO receptor-matrix fetch (in flight); if the sandbox stays slow,
  run it on BMRC via the fire-and-forget scripts. Deliver `ko_receptor_DE.npz` +
  `_meta.parquet` to `from_B/`. Then (optional) the replication cohort.
- **A:** the moment the KO matrix lands — CLR-center it in receptor space, run
  `match_engine.py` against **both** B's blood-referenced conv target (retention/entry)
  and the Treg target, and produce the KO-ranking figure + `ko_ranking.csv`.
- **Joint headline claim to aim for:** "Against a true circulating reference,
  tumor-infiltrating CD4s downregulate egress (S1PR1/CX3CR1) and upregulate
  tissue-entry receptors (CCR6/CXCR5); knockouts of [X] reproduce this shift and are
  nominated as brakes on infiltration/retention."
