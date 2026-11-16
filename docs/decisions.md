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

## 2026-11-16 — Systematic literature search done; scoop risk closed

**The specific question is unclaimed.** Full record, with queries and hit counts, in
`docs/literature-search.md`. Europe PMC returns zero papers with both "blood-brain
barrier" and "applicability domain" in the title, and zero for BBB + chemical space
+ coverage/overlap at abstract level. 35 unique candidate records were identified and
all 35 abstracts read; four adjacency risks read in full. Every citation was verified
against the Europe PMC API rather than taken from a search snippet — one web-search
result supplied a PMC ID that does not resolve.

**The framing sharpened, and this is the main outcome.** Every AD analysis in this
literature is run on the model's own held-out test set, so all of them report ~94%
in-domain coverage (93.9%, 94.8%, "complete coverage" in three separate 2026
papers). That number is near-guaranteed by construction and says nothing about
deployment. Our 85.8% out-of-domain for BACE1 is its inverse. The contribution is
not "out-of-domain predictions are worse" — that is already established — but that
the field certifies domain coverage on a population no screening pipeline meets.

**A prior result now supplies our premise.** Pharmaceutics 2026
(10.3390/pharmaceutics18060670) reports in-domain R² = 0.641 vs out-of-domain
R² = 0.164 on a B3DB logBB model. This is the cost of being out of domain, measured
on our own dataset, and it means we no longer have to establish that ourselves —
we establish the exposure. Caveat: their out-of-domain figure rests on 13 compounds.

**A prior null result cuts against us and must be cited, not buried.** Comput Biol
Chem 2026 (10.1016/j.compbiolchem.2026.109356) found a 0.32–0.39 AUC generalisation
gap while AD analysis showed complete structural coverage, concluding that
out-of-domain extrapolation did not explain it. This is direct evidence for the
"distance may not predict error" risk already logged, and it hardens the design
constraint: error gets measured directly in AChE-proximal space, never inferred
from distance.

**New curation requirement.** A 2026 preprint (10.20944/preprints202609.2002.v1)
shows deduplicating B3DB on canonical SMILES finds only 3 duplicates, while
InChIKey-skeleton deduplication collapses 7,802 compounds to 3,952 and exposes 131
skeletons carrying discordant BBB+/BBB- labels. Our curation must deduplicate on
skeleton and report the discordant count. The scoping numbers in `README.md` were
computed without this and will need recomputing once curation is fixed.

**Abandoning the original idea is confirmed correct.** Benchmark inflation and
split sensitivity on B3DB are now covered by that preprint plus
10.3390/pharmaceutics18081018, on top of the two papers already logged.

**Residual risk accepted as low.** Europe PMC does not fully index ChemRxiv or the
ACS/Wiley/RSC back catalogue at abstract level, and a scoop could sit in a methods
section whose abstract advertises something else. Re-run the two zero-hit queries
before submission.

**Next.** Write the pre-registration. It is now unblocked: the question is
confirmed unclaimed, the framing is fixed, and three design constraints above
(skeleton deduplication, direct error measurement, exploratory-numbers disclosure)
are settled going in.

## 2026-11-16 — Skeleton-level curation applied; headline holds, gate tightens

Done before writing the pre-registration, so that the pre-registered numbers are
ones that will not move. Script `scripts/curate_gate.py`, output
`results/curated_overlap.txt`, which supersedes `scoping_overlap.txt`.

**Curation decision, now settled.** Deduplicate both B3DB and the ChEMBL target
sets on the first block of the InChIKey (connectivity only; drops stereochemical
and protonation layers). Rationale: canonical-SMILES deduplication finds **0**
duplicates in B3DB, because SMILES distinguish stereoisomers that 2D Morgan
fingerprints cannot. Deduplicating on anything finer than the skeleton is
incoherent for a fingerprint-based model.

**Effect on B3DB.** 7,805 parsed records collapse to 4,022 skeletons; 1,488
skeletons have multiple members, largest group 9. 130 skeletons carry both BBB+
and BBB- labels. Discordant skeletons are **excluded from the labelled reference
set** (contradictory ground truth) but **retained for domain-coverage geometry**,
where only structure matters. Labelled reference set: 3,892 compounds, 2,472 BBB+
and 1,420 BBB-. Target sets: BACE1 7,481 -> 6,918; AChE 3,125 -> 3,014.

**Pipeline independently reproduces the published counts.** We get 4,022 skeletons
and 130 discordant labels; the preprint reports 3,952 and 131 from 7,802 records.
Small differences are expected from parse-failure handling and RDKit version. This
is a genuine check that our curation does what we think it does.

**The headline is robust — this was the main thing to find out.** BACE1
out-of-domain at 0.3 moves 85.8% -> 86.0%; AChE 26.4% -> 26.8%. Medians essentially
unchanged. The BACE1/AChE contrast is not a deduplication artefact, and the
pre-registration can quote these numbers.

**The feasibility gate tightened, and this matters for the design.** Labelled
ground truth within 0.35 of AChE chemistry falls from 942 to **611** compounds
(464 BBB+, 182 BBB-); within 0.4, from 458 to 300. For BACE1, from 145 to **101**
at 0.35 and 49 to **28** at 0.4. The earlier "~942 labelled compounds" figure in
the 2026-11-14 entry is superseded. AChE remains a viable positive control, but the
error analysis must be powered for ~600 compounds with 2.5:1 class imbalance, not
~950. BACE1 remains unmeasurable, as before.

**This is a second finding, not just a correction.** The labelled data sitting
nearest to target chemistry is disproportionately stereoisomer-redundant — roughly
a third of it collapses. So apparent ground-truth coverage near target space is
itself inflated, on top of being thin. Worth a paragraph in the paper.

**Scaffold overlap is starker after curation.** BACE1 shares 14 Bemis-Murcko
scaffolds with B3DB out of 2,591, and exactly 1 identical skeleton. AChE shares 36
of 1,493, and 27 identical skeletons.

**Environment note.** The venv was absent and was rebuilt; rdkit 2025.09.2 /
pandas 2.3.3 / Python 3.9.6, identical to the 2026-11-15 run, so the raw-vs-curated
comparison is not confounded by library versions. `data/` had survived.
