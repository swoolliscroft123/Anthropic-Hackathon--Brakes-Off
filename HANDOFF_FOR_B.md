# HANDOFF → Session B (portable, self-contained)

You (Session B, another Claude Science / Opus session on a second machine) are
collaborating with **Session A** on a shared analysis. You are in a **different
project**, so you cannot see A's artifacts or frame — everything you need is in
THIS file plus the two attached data files. Work entirely from these.

**Attached with this brief (ask the user for them if missing):**
- `receptor_panel_v1.json` — the 33-gene receptor panel (shared coordinate system)
- `cd4_compartment_map.json` — CD4 subset → compartment map (which clusters are Treg etc.)

---

## Project goal
Nominate druggable **brakes** on tumor infiltration by matching CRISPR Perturb-seq
knockout signatures (in human CD4⁺ T cells) against the receptor-repertoire shift
that real tumor-infiltrating CD4s show — computed in **receptor space** on
**compositional (CLR) fingerprints**.

## Why you exist / your task (CRITICAL PATH)
Session A built the target direction from the Zheng 2021 atlas (GSE156728) but hit a
wall: **that deposit has no clean peripheral blood for solid tumors** (blood = 4
patients, all heme/CHOL). A used adjacent-normal→tumor as a stand-in, and found:
- **Treg confound:** 90% of CCR8⁺ tumor CD4s are Tregs; the naive "homing" signal was
  suppressive-compartment composition, not anti-tumor cells rewiring receptors.
- After excluding Tregs AND controlling for subset composition, the surviving signal
  is **egress/recirculation receptors going UP in tumor (S1PR1, CCR7, SELL, S1PR4)** —
  but this is entangled with the fact that adjacent-normal CD4s are more terminally
  tissue-resident (egress fully off). So A can't tell "cells actively leaving tumor"
  from "normal-tissue reference is just extra-resident."

**Your job: build a TRUE circulating→tumor target direction** so the polarity is clean
(real infiltration vs egress-artifact). Fetch + harmonize a paired-blood solid-tumor
CD4 scRNA cohort with P (blood) / N (adjacent-normal) / T (tumor) triads.

**Candidate cohorts (the ones Zheng integrated — all have CD4 P/N/T):**
- Guo 2018, NSCLC — GEO **GSE99254**
- Zhang 2018, CRC — GEO **GSE108989**
- Zheng 2017, HCC — GEO **GSE98638**
(Pick whichever ingests cleanest; NSCLC/GSE99254 is a good first target.)

## Deliverable (hand back to A via the user)
A file **`blood_ref_delta_within_subset.parquet`** — a pandas DataFrame indexed by the
33 panel genes with columns `delta, frac_up, p, fdr`, representing the within-subset
**blood→tumor** CLR shift. Plus a 1-paragraph note on which cohort/how many pairs.
Save it as an artifact in YOUR project and tell the user; they'll relay the file to A.

## METHOD RECIPE — follow EXACTLY so A's and your Δ are comparable
1. **Panel** = the 33 genes in `receptor_panel_v1.json` (HGNC symbols), this fixed order:
   CXCR3, CXCR6, CCR5, CXCR4, CCR8, CCR2, CCR6, CX3CR1, CCR7, CXCR5, CCR4, CCR10, CCR9,
   CCR1, CCR3, XCR1, ACKR1, ACKR2, ACKR3, ACKR4, GPR183, GPR15, S1PR1, S1PR4, S1PR5,
   SELL, SELPLG, ITGA4, ITGAE, ITGAL, ITGB1, ITGB2, ITGB7.
2. **CD4 only.** Use the cohort's own CD4 subset labels; map Treg-like clusters using
   the categories in `cd4_compartment_map.json` (FOXP3/IL2RA-hi clusters = suppressive).
   For the PRIMARY target compute within the **anti-tumor + conventional** compartments
   (exclude Treg), but ALSO save a Treg-only version if labels allow (Arm B).
3. **Pseudobulk**: sum raw counts per **(patient × subset × loc)**, loc ∈ {P,N,T}.
4. **CLR**: (counts+0.5) → row-normalise to proportions over the 33 genes → log →
   subtract the per-profile mean of the 33 log-values.
5. **Δ (within-subset, paired)**: for each (patient × subset) with ≥20 cells on BOTH
   sides, Δ = CLR(T) − CLR(P)  [blood→tumor]. Also save CLR(T) − CLR(N) if you want to
   cross-check A's normal→tumor. Average Δ over all (patient×subset) pairs.
6. **Stats**: Wilcoxon signed-rank across pairs per gene; BH-FDR over the 33 genes.
7. Return the DataFrame described above. Keep a per-pair matrix too if easy
   (`blood_ref_delta_perpair.parquet`), same as A's `..._perpair` products.

## What A is doing meanwhile (so you know the join point)
- A built + unit-tested `match_engine.py`: scores each KO's Δ_KO vs a target Δ by
  cosine + signed projection + gained/lost decomposition, with a permutation null and
  KO'd-gene hold-out. **It is target-agnostic** — A drops YOUR `delta` vector in as the
  target and ranks knockouts. So the interface is: your parquet's `delta` column,
  indexed by the 33 genes in the order above.
- A also computed an Arm-B (anti-Treg) target and found CCR8 is NOT a within-Treg
  tumor-gain (it's a Treg-identity marker) — so if your cohort has Tregs, checking
  whether CCR8 behaves the same way with a real blood reference is a valuable cross-check.

## Sync discipline
- You and A are on separate stores; the **user relays files** between you. When you
  finish, name the file exactly as above and tell the user "ready for A."
- If you change the method or discover a blocker, write it at the top of your reply so
  the user can carry it back to A.
