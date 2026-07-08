# SYNC BRIEF — two-session coordination

**Project:** `proj_56a68a31904c` (both sessions live here → shared artifact store).
**Session A (this one):** frame `bf0af305-cec3-4f7c-b8c9-4576468b5058`.
**Session B (other machine):** paste its frame_id here on first sync ↓
- Session B frame_id: `__________________________`
**Last updated by:** A · **Brief version:** 1

---

## 0. How the two sessions stay grounded & aware (READ FIRST)

There is **no live channel** between sessions. Coordination is through the shared project:
1. **Shared artifacts** — everything either session saves is visible to the other via
   `host.artifacts()` (same project). IDs are in §5. This is the source of truth for data.
2. **Read the other's work** — in the `repl` tool:
   `host.frames(frame_id="<other frame>")` → full transcript;
   `host.frames(project_id="proj_56a68a31904c", pattern="<keyword>")` → search both.
3. **This brief is the baton.** Whoever changes plan or finishes a task re-saves
   SYNC_BRIEF.md as a **new version of the same artifact** (`version_of`), bumps the
   version number + "last updated by", and notes it in §4 log. The other session
   re-reads it at the start of each work block.
4. **Ownership rule to avoid clobbering:** a data product is owned by whichever
   session's task (§3) produces it. Don't overwrite the other's artifacts; save your
   own filenames. Only SYNC_BRIEF.md is co-edited (always via version_of, never parallel).

---

## 1. Project goal (unchanged)

Mine genome-scale CRISPR Perturb-seq in human CD4⁺ T cells to nominate druggable
**brakes** on tumor infiltration: genes whose KO reshapes a CD4 T cell's
chemokine/homing-receptor repertoire toward the tumor-relevant state, matched in
**receptor space** on **compositional (CLR) fingerprints**.
Full design: `pipeline_design.md` (§5).

## 2. State of play — what is DECIDED and what we FOUND

**Data anchors**
- Perturbation arm (Δ_KO): genome-scale Perturb-seq, primary human CD4⁺ T, 4 donors,
  rest+stim (Zhu/Dann/…/Marson, bioRxiv 2025; CZI Virtual Cells Platform). NOT YET INGESTED.
- Target arm (Δ_tumor): pan-cancer T-cell atlas GSE156728 (Zheng 2021). INGESTED for
  CD4, 5 solid cancers (BC/ESCA/RC/THCA/UCEC), 58,892 cells, 33-gene receptor panel.

**Receptor-space panel v1** — 33 genes (16 chemokine R, 8 adhesion, 5 lipid incl.
GPR183/EBI2+S1PRs, 4 atypical). Pre-registered. `receptor_panel_v1.json`.

**KEY FINDINGS (the confound cascade — this is why the target direction is hard):**
1. **No clean blood in GSE156728.** Peripheral blood = 4 patients, all heme/CHOL →
   can't build solid-tumor blood→tumor from this deposit. Chose adjacent-normal→tumor
   (34 paired pts) instead. [n=31 usable after ≥25-cell filter, 5 cancers]
2. **Treg confound is severe.** Tregs 14%→35% of CD4 on tumor infiltration; **90% of
   CCR8⁺ tumor CD4s are Tregs.** Naive Δ_tumor rank #1 = CCR8 was suppressive-compartment
   composition, not anti-tumor homing. Fig: `treg_confound.png`.
3. **Composition, not per-cell rewiring, drives the naive signal.** Excluding Tregs
   AND controlling for subset composition (within-subset Δ) collapses the "homing"
   hits. What survives (FDR<0.1): **S1PR1↑, CCR7↑, SELL↑, S1PR4↑** = lymph-node
   egress/recirculation receptors going UP in tumor.
4. **Egress signal is real but MODEST and residency-confounded.** In absolute CLR,
   S1PR1 stays rank ~17/33 in both normal & tumor; only CCR7 climbs (13→8). Adjacent-
   normal CD4s are more terminally tissue-resident (egress fully off); tumor CD4s
   retain more egress machinery. So "tumor>normal egress" is partly a residency floor,
   not proof cells are streaming out.

**Interpretation shift (user, session A):** the honest signal points toward
**retention/egress** biology, not trafficking-in. This reframes candidate brakes as
"keep anti-tumor CD4s IN the tumor" rather than "bring them in."

## 3. CURRENT PLAN + division of labor

**User decision (this turn): get a TRUE blood reference first** — to disambiguate
real egress vs residency-floor and restore a clean circulating→tumor polarity.

- **Session B (new machine) — CRITICAL PATH: blood reference.**
  Fetch + harmonize a paired-blood solid-tumor CD4 scRNA cohort (candidates: the
  constituent cohorts Zheng integrated — e.g. Guo 2018 NSCLC (GSE99254), Zhang 2018
  CRC (GSE108989), Zheng 2017 HCC (GSE98638) — all have P/N/T triads on CD4).
  Deliverable: `blood_ref_delta_tumor_within_subset.parquet` — the circulating→tumor
  Δ in the SAME 33-gene panel, SAME CLR + within-subset method (mirror A's recipe from
  the lineage of `delta_tumor_within_subset.parquet`). Save + note in §4.
- **Session A (this machine): Perturb-seq matching machinery + anti-Treg arm.**
  (a) Build the KO→Δ_KO pipeline (CLR in receptor space, KO'd-gene held out) ready to
  plug in whichever target vector wins. (b) Scaffold the anti-Treg arm (Arm B): target =
  the CCR8-hi suppressive program; desirable KO pushes cells AWAY from it. (c) Provide B
  the exact method recipe so both Δs are computed identically.

**Convergence:** once B's blood-referenced target lands, A scores KOs against BOTH the
retention (down-egress) target and the anti-Treg target; report where they agree.

## 4. Sync log (append newest at top)
- v2 · A · Built + unit-tested the **matching engine** (`match_engine.py`): cosine +
  signed projection + gained/lost decomposition + permutation null + KO'd-gene hold-out.
  Target-agnostic → plugs into whichever Δ_target B's blood reference yields. Passes
  self-test (planted match ranks #1, anti-match last, circularity trap neutralized).
- v2 · A · Computed **Arm B target** (within-Treg normal→tumor, `armB_treg_target_within_subset.parquet`).
  IMPORTANT cross-check for B: **CCR8 is only rank 10 / n.s. (Δ=0.25, FDR=0.13)** in the
  within-Treg contrast — i.e. CCR8 marks Treg-vs-nonTreg identity, NOT something a Treg
  gains on tumor entry. The within-Treg shift (S1PR1↑ CXCR3↑ ITGAE↑ SELL↑) is the SAME
  egress/residency axis seen in the anti-tumor compartment → the adjacent-normal reference
  yields a compartment-NONSPECIFIC tissue-adaptation axis, not a suppression program.
  This independently confirms the blood reference (B's task) is the right call.
- v1 · A · set up brief, manifest, division of labor. Awaiting B to claim blood-ref task
  and paste its frame_id above.

## 5. Artifact manifest (real version_ids in this project)
Load any with `read_file(version_id=…)` or `host.artifact_path(vid)`.

| file | version_id |
|---|---|
| pipeline_design.md | fb022349-ba46-4021-b06e-1ddb60a6612a |
| receptor_panel_v1.json | 57378967-f9e0-4342-813c-668d8e48062a |
| receptor_panel_v1.csv | 19783298-a1b1-4811-a8d8-a565ff4b26d3 |
| cd4_compartment_map.json | 6addd19a-536b-471a-bdd7-e03acf9f8f6a |
| atlas_delta_tumor.parquet | 3c6ad7d0-da8e-44ab-a0d7-4e54d8d56e17 |
| atlas_delta_tumor_stats.csv | 9a7d745b-98c4-4441-8db0-f66e1b7e7e9f |
| atlas_delta_tumor_perpatient.parquet | 29179659-322c-4284-891b-bd12da99a1a6 |
| atlas_pseudobulk_counts.parquet | 2a998d5b-11a3-4e47-bd05-b9e5de059f1b |
| atlas_pseudobulk_meta.parquet | 8c54dac0-3cce-44bf-b688-3af28429b1df |
| delta_tumor_antitumor.parquet | ce1b50af-9dcc-4216-bfeb-76e0c47d53d9 |
| delta_tumor_within_subset.parquet | e4692856-fd1d-417b-8be0-91f689803911 |
| delta_tumor_within_subset_perpair.parquet | 8e3b14e0-cd48-41fe-a096-002edf25d8d4 |
| treg_confound.png | afcd7f34-4933-4c51-b759-fe8e320afbad |
| delta_tumor_target_direction.png | 0d4538e5-c05c-456f-9c78-10db71762747 |

## 6. Method recipe (so both sessions compute Δ identically)
1. Panel = 33 genes in `receptor_panel_v1.json` (HGNC symbols).
2. Per-cell counts → pseudobulk by summing raw counts per **(patient × subset × loc)**.
   Subset labels = atlas `meta.cluster`; compartment map in `cd4_compartment_map.json`.
   Anti-tumor compartment = effector(GZMK/GZMA/CCL5/CX3CR1) + helper(Tfh CXCR5,
   TfhTh1 CXCL13, Th17). EXCLUDE all 4 Treg clusters from Arm A.
3. CLR transform: (counts+0.5)→proportions→log→subtract per-profile mean over the 33.
4. Δ = within-**(patient×subset)** paired [CLR(tumor/target) − CLR(reference)], require
   ≥20 (blood/normal) cells & ≥20 tumor cells per side; average over pairs.
5. Significance: Wilcoxon signed-rank across pairs, BH-FDR over 33 genes.
6. Match Δ_KO to target Δ by cosine + signed projection in the 33-dim space;
   permutation null; hold out the KO'd gene if it's in the panel.
