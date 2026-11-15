# Decision log

Dated record of real decisions and status changes, newest last. A collaborator — or a
different Claude session — should be able to pick up the state of the project from
this file without re-deriving it.

## 2026-11-14 — Project scoped, not yet started

**Topic chosen.** Applicability domain of blood–brain barrier (BBB) predictors in
Alzheimer's target chemical space. Two-part design: (1) validity audit of BBB
predictions for BACE1 and acetylcholinesterase inhibitor space; (2) an
acetylcholinesterase-focused candidate shortlist produced using only in-domain
predictions, with synthetic accessibility assessed.

**An earlier version of this project was abandoned.** The first plan was to show that
random train/test splits inflate BBB model performance. Rejected after literature
check: published twice already (JCIM 2025, "Overrepresentation Bias Leads to
Performance Overestimation in BBB Permeability Prediction Models"; Pharmaceutics 2026,
3D conformer descriptors on B3DB), and the effect size is ~0.00–0.03 AUC, sometimes
within run-to-run variance. Not enough to carry a paper.

**Scoping check run before committing.** Verified that the datasets exist, are
licensed for use, and contain enough data for the design. Results in
`results/scoping_overlap.txt`. Key numbers in `README.md`.

**Feasibility gate: passes for AChE, fails for BACE1.** Error can be measured in
AChE-proximal space (~942 labelled compounds above 0.35 similarity, both classes
represented). It cannot for BACE1 (145 at 0.35, 49 at 0.4, all weak matches). This
converts into the paper's sharpest claim rather than killing it: for BACE1 chemical
space there is essentially no public BBB ground truth, so published filters applied
to BACE1 hits are unvalidatable with existing data.

**Data versions.** B3DB fetched from GitHub `main` on 2026-11-14 (7,805 compounds
parsed: 4,956 BBB+, 2,849 BBB−). ChEMBL_37, released 2026-05-01, queried via API:
7,481 unique BACE1 actives, 3,125 AChE actives.

**Placeholder decisions awaiting a chemist's judgement.** These were chosen to get
numbers, not because they are right:
- Activity threshold: pChEMBL ≥ 6 on IC50/Ki only. ChEMBL mixes assay types, units
  and conditions; which measurements are comparable is a real decision.
- Representation: Morgan fingerprints, radius 2, 2048 bits.
- Domain definition: nearest-neighbour max Tanimoto. Leverage and Mahalanobis
  distance are alternatives and give different answers.

**Pre-registration constraint.** The scoping analysis above has already been run, so
those overlap numbers are exploratory and the pre-registration must state this
explicitly. The modelling and error analysis has not been touched and is what gets
pre-registered.

**Collaborator.** Sam, Davidson junior, chemistry major, works in a lab (bench access
not assumed and not required). Pitch document written and shared for his decision.
Python experience unknown — determines whether he owns the representation code or we
pair on it.

**Open before week 1.**
- Systematic literature search to confirm the specific question is unclaimed. Three
  targeted searches found nothing, which is suggestive, not conclusive.
- Target journal decided. Leading candidate: *Journal of Cheminformatics* (BMC /
  Springer Nature). APC figures from third-party listings conflict (~€1,790–1,990 /
  $2,190–2,290) and waiver terms were not found; read the publisher's own fees page.
- APC hardship waiver route: signed letter from the sponsored-programs office
  confirming no funding. Precedent exists with this publisher.
- Confirm Sam is in, and settle authorship in writing.
