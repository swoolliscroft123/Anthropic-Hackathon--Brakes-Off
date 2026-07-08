# BRIEF FOR A — in-vivo validation anchor + reframe (from B)

**Source:** Liu, Carnevale et al. (UCSF), *"In vivo genome-wide CRISPR screens in
human T cells to enhance T cell therapy for solid tumors"*, bioRxiv
10.1101/2025.09.23.678127 (2025). Corresponding authors Qi Liu & Julia Carnevale;
A. Marson is a senior co-author. (Same institution as the `marson2025_data`
Perturb-seq deposit we're mining, but a distinct study.)

## Why this matters
The user flagged a possible scoop. I read the paper end-to-end. Verdict: **it does
NOT overlap our method and instead gives us an independent in-vivo answer key.**

What they did: two phenotypic genome-wide CRISPR KO screens in *mouse-resident,
healthy-donor* human T cells — one for intratumoral **abundance** (infiltration), one
for **IFN-γ**. Hits analysed by MAGeCK + GO-term GSEA.

What they did NOT do (literal full-text search):
- **No Perturb-seq** — the word appears once, in the Discussion, as *future work*
  ("linked to single-cell transcriptional states via Perturb-seq").
- **No patient-TIL analysis** — "screen TIL from cancer patients" is also named as
  *future work*. Their data are healthy-donor T cells in mice.
- **No single-cell RNA-seq, no receptor repertoire, no compositional/CLR analysis,
  no GEO patient atlases.** Zero methodological overlap with our pipeline.

So our lane — matching Perturb-seq KO signatures to **real human patient TIL receptor
repertoires** in compositional space — is untouched, and the authors explicitly list
both halves of our approach as things they haven't done.

## The convergence (this is the win)
Their infiltration-screen trafficking hits (paper p6-p7, verbatim):
**S1PR1, GNA13, CXCR4, ARHGEF1, PTGER4, P2RY8** — the P2RY8–Gα13 GPCR pathway, whose
cited mechanism is the **S1PR1 egress/retention axis** (their refs 27-28: S1P1
promotes egress; S1PR1 desensitisation lets lymphocytes "overcome their attraction to
blood" — Arnon et al. Science 2011).

That is our blood-referenced result from the opposite direction: we found successful
TILs **downregulate the egress axis (S1PR1, S1PR4, S1PR5)**. Two orthogonal assays,
two systems, one axis.

## Concrete ask for the engine run
When you run `match_engine.py` against B's blood-referenced conv target
(`blood_ref_delta_within_subset.parquet`), please **report where these in-vivo hits
rank** — this is a pre-registered concordance test:

- **Primary trafficking answer key:** `P2RY8, GNA13, ARHGEF1, S1PR1, CXCR4, PTGER4`
- Report each gene's rank + percentile in the KO ranking, and a rank-based enrichment
  p (e.g. Mann–Whitney of answer-key ranks vs all KOs, or a simple GSEA-style ES).
- **Interpretation:** high concordance ⇒ our receptor-space method provably recovers
  in-vivo-validated infiltration brakes. Top-ranked KOs that are NOT in their screen
  ⇒ candidate novel receptor-rewiring hits (their abundance screen is blind to
  composition changes that don't alter bulk counts).
- **Mechanistic sub-question:** if P2RY8 ranks high phenotypically (theirs) but LOW in
  our receptor-space score, our axis is capturing a complementary mechanism — worth
  noting either way.

Note: only genes present in the Perturb-seq var (10,282) can be scored. P2RY8/GNA13
were confirmed present in a synthetic-schema test; verify in the real matrix.

## Reframe (for the writeup)
From "discover a novel infiltration gene" (dead — they're first) to **"a
patient-anchored compositional method that recovers in-vivo-validated GPCR-trafficking
brakes and extends them with receptor-rewiring hits."** The paper becomes our
validation set, not our competitor.
