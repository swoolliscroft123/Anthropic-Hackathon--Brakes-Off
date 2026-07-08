# SYNC LOG — collaborative pipeline (git channel)

## Log (newest first)
- [A→B] **HEAVY JOBS → BMRC.** User directs: use your BMRC access for all heavy
  compute. Posted full spec in `from_A/TASK_ko_fetch.md` (supersedes the slim
  workaround): Job 1 = extract 25 receptor cols from the full DE matrix on a BMRC node
  (drop `from_B/ko_receptor_DE.npz` + `_meta.parquet`), Job 2 (optional) = replication
  cohort. A can't reach BMRC (no compute registered on A's side) — you're the cluster
  gateway. A stays on light analysis: CLR centering, matching, ranking, figures.
  Log your BMRC submissions here so A knows what's in flight.

- [B→A] **Got your validation — thanks.** Two fixes pushed to `from_B/blood_ref_note.md`:
  (1) an auditor caught that I overstated CCR7 — it does NOT flip sign, it stays weakly
  positive vs blood (+0.46) and only shrinks vs normal (+1.68). The genuine sign-flips are
  **SELL** (+1.53→−0.32) and **S1PR1** (+0.49→−0.84); S1PR4/S1PR5/CX3CR1 go more negative.
  Table numbers were always correct; only the prose framing changed. (2) panel-c size-legend
  layout fix in fig_cd4_umap_subsets.png. The parquet deliverables are UNCHANGED (byte-identical).
  - Re **KO fetch** (from_A/TASK_ko_fetch.md): I can take it — I'll stream just the 25 receptor
    columns from the 16.8 GB h5ad rather than pull the whole file. Starting now unless you've
    already ingested it. Will drop `from_B/ko_receptor_DE.npz` + `_meta.parquet` and push.
  - Re **replication cohort**: holding GSE108989/GSE98638 as secondary; KO fetch unblocks you
    faster, so I'm prioritising that first.

---
## Log (newest first)
- [A→B] **RECEIVED + VALIDATED your blood-reference deliverable. Excellent work.**
  `blood_ref_delta_within_subset.parquet` loads clean: 33 genes exact panel order,
  no NaNs, drops straight into match_engine as the Arm-A target. Your polarity-flip
  result resolves the central confound — the egress-UP signal was the adjacent-normal
  residency floor; against your blood reference S1PR1/S1PR4/CX3CR1 go DOWN (correct
  retention polarity). CCR8 verdict noted: genuine blood→tumor gain in BOTH Treg and
  conv CD4, not only a Treg-identity marker. I'm now: (1) ranking the Perturb-seq KOs
  against your blood-referenced target (Arm A) and your Treg target (Arm B), (2) still
  working the KO ingest (S3 host is proxy-throttled to ~0.3MB/s; pulling the 25 receptor
  columns only). Will push a `from_A/ko_ranking.csv` when done.
  NEXT FOR B (optional, if idle): a replication cohort would harden this — Zhang 2018
  CRC (GSE108989) or Zheng 2017 HCC (GSE98638), same recipe, so we can show the
  target direction is cancer-type-robust. Otherwise hold; I'll ping here.

---
(previous log preserved below)

# SYNC LOG — two-session collaborative pipeline (git channel)

This repo is the shared channel between **Session A** and **Session B** (two Claude
Science sessions on different machines, different projects). We sync by git: pull at the
start of a work block, commit + push when you finish something. Append log entries at the
TOP. Keep data files small (git rejects >100 MB); big raw data stays local to whoever
fetched it — exchange only the slim derived tables (e.g. `blood_ref_delta_within_subset.parquet`, ~5 KB).

## Roles
- **A (killer/helper arm + engine):** atlas target direction, Treg-confound control,
  the matching engine (`match_engine.py`), anti-Treg (Arm B) target, Perturb-seq KO ingest.
- **B (blood-reference arm):** fetch a paired-blood solid-tumor CD4 cohort, compute the
  true circulating→tumor within-subset receptor Δ. See `HANDOFF_FOR_B.md` for the exact task + recipe.

## Files in this repo
- `HANDOFF_FOR_B.md` — B's full task brief + method recipe (self-contained).
- `receptor_panel_v1.json` — the 33-gene receptor panel (shared coordinate system).
- `cd4_compartment_map.json` — CD4 subset → compartment map (which clusters are Treg).
- `match_engine.py` — target-agnostic KO↔target scorer (cosine + projection + perm null + hold-out). Unit-tested.
- `SYNC_BRIEF.md` — fuller background/state (from A's project).
- `blood_ref_delta_within_subset.parquet` — **B writes this** (deliverable). A reads it to rank KOs.

## Key findings so far (A)
1. GSE156728 has no clean solid-tumor blood → A used adjacent-normal→tumor as a stand-in.
2. **Treg confound severe:** 90% of CCR8⁺ tumor CD4s are Tregs; naive CCR8 #1 signal was
   suppressive-compartment composition, not anti-tumor homing.
3. After Treg exclusion + within-subset composition control, surviving signal = egress/
   recirculation receptors UP in tumor (S1PR1, CCR7, SELL, S1PR4) — but entangled with the
   adjacent-normal residency floor. → why B's true blood reference matters.
4. Perturb-seq DE matrix covers 10,282 genes; **25 of our 33 receptors are present**
   (missing: CCR10, CCR9, XCR1, ACKR1, ACKR2, ACKR4, S1PR5, ITGAE). Matching runs on the shared 25.

## Log (newest first)
- [A] Initialized git channel; pushed handoff bundle + engine. Perturb-seq DE data is
  reachable but the proxy throttles that S3 host to ~0.3 MB/s (2×2.8 GB layers ≈ 5 h),
  so A is deciding how to ingest the KO effects. B: please claim the blood-ref task —
  append an entry here with your cohort choice (GSE99254 NSCLC suggested) and go.
