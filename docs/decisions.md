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

## 2026-11-16 — Pre-registration v1.0 written

`docs/preregistration.md`. Written after curation so that its numbers are ones that
will not move, and before any model has been trained.

**Primary design settled: proximal holdout versus matched random holdout.** Remove
from training every labelled B3DB compound within 0.35 of AChE chemistry (n = 611),
train on the remainder, evaluate on the held-out proximal set; compare against a
size- and class-matched random holdout over 200 draws, and against a holdout
propensity-matched on MW, cLogP and TPSA. Training-set size is identical across arms
by construction.

**The property-matched arm exists for a real reason.** Target-proximal compounds are
larger and more lipophilic than B3DB's average (BACE1 mean MW 472 vs BBB+ 318), so a
performance drop could reflect molecular complexity rather than domain novelty. If
the simple and property-matched controls disagree, the property-matched one governs
the conclusion. Without this arm a reviewer would be right to reject the inference.

**Primary endpoint:** ΔROC-AUC, ECFP4 random forest, proximal versus
property-matched holdout. One endpoint, one model, one control. Everything else is
secondary and labelled so.

**Calibration added as a secondary endpoint.** A filter that is merely
miscalibrated out of domain still misranks compounds even when its AUC holds, which
is the practically relevant failure for a screening cutoff.

**Power computed, not asserted.** `scripts/power.py`, output `results/power.txt`.
At the curated 464/182 split the minimum detectable ΔAUC is **≈0.053** at 80% power.
Stated bluntly in the pre-registration: if the true degradation is 0.01-0.03 AUC we
will not detect it, and a null must be reported as "no effect larger than ~0.05",
not as no effect. The abandoned predecessor idea died on an effect of 0.00-0.03 AUC,
so this is a live possibility and is on the record in advance.

**Decision rules pre-specified**, including what counts as refutation (ΔAUC CI
within ±0.03, reported as a null in those words, corroborating
10.1016/j.compbiolchem.2026.109356) and what counts as inconclusive. No outcome
licenses switching endpoint, cutoff, model or target.

**BACE1 declared unmeasurable in advance** against a stated sufficiency criterion
(≥200 labelled compounds, ≥50 per class at 0.35). AChE passes at 611; BACE1 fails at
101, where the minimum detectable ΔAUC would be ≈0.124. Recording this before
attempting it converts a dead end into a stated finding.

**Component 2 (AChE shortlist) is declared exploratory and hypothesis-generating**,
with no claim of activity, brain penetration or therapeutic potential, and
causal/efficacy language excluded. No bench work proposed or required.

**Blocked on one thing:** the activity threshold (pChEMBL ≥ 6 on IC50/Ki) is still
provisional pending the chemistry co-author's judgement on assay comparability. If
it changes, the pre-registration is amended and dated before analysis runs. This is
now the critical path.

## 2026-11-16 — Curation decided from literature, not from a co-author

The second author is a chemistry major but not an enzyme-kinetics specialist, so the
"placeholder decisions awaiting a chemist's judgement" from 2026-11-14 could not be
resolved that way. They are now made from published curation standards and verified
empirically. Full reasoning and citations in `docs/curation-decisions.md`.

**Consequence for the manuscript, stated so it is not forgotten.** These decisions
are defended by citation and sensitivity analysis, not by expert assertion. The
paper must not imply specialist kinetics review that did not happen. Author roles in
the pre-registration were amended accordingly.

**The literature genuinely disagrees.** Kalliokoski et al. 2013
(10.1371/journal.pone.0061007) find pooling IC50 with Ki acceptable given a ~0.35
log offset; Landrum & Riniker 2024 (10.1021/acs.jcim.4c00049) find ~65% of paired
measurements differ by >0.3 log units and advise against casual pooling. Both are
about the accuracy of potency values.

**That controversy does not reach us, and we can show it rather than argue it.** No
potency value enters any model; the threshold decides set membership only. We
measured the replicate spread in our own data (BACE1 46.9% span >0.3 log units,
18.1% >1.0; AChE 34.0% and 17.2%) — the concern is real and present — and then
measured whether it matters. Across ten curation variants BACE1 out-of-domain spans
81.8-89.4% and AChE 21.8-36.4% at the 0.3 cutoff. **Worst case for the contrast
still leaves a 45-point gap.** `results/sensitivity.txt`.

**Decisions, in brief.** Pool IC50 and Ki with no offset, exclude Kd; assay
confidence score 9 only; assay type B; pChEMBL >= 6 with the 5-8 sweep reported;
replicates aggregated by median pChEMBL; no per-target threshold. Four further
filters (standard_relation, data_validity_comment, units, organism) are asserted in
code but verified to be no-ops in ChEMBL_37, and are recorded as such so nobody
later mistakes them for the filters that mattered.

**The confidence-score filter is the one that does real work, and the data decided
it.** Score-9 assays are 100% Homo sapiens for these targets; score-8 assays have
assay_organism unspecified or non-human (Cercopithecidae, Cavia porcellus), matching
relationship_type H. This matters most for AChE, where Electrophorus and Torpedo
enzyme assays are common and have different inhibitor SAR. Cost: 29.2% of BACE1 and
19.3% of AChE records. Verified by inspecting the assays, not assumed.

**New primary sets, superseding all earlier counts.** BACE1 5,157 actives
(85.8% / 97.5% / 99.4% out-of-domain at 0.3 / 0.35 / 0.4); AChE 2,391 actives
(28.4% / 58.3% / 77.2%).

**The feasibility gate tightened again, and the power with it.** Labelled B3DB
compounds within 0.35 of AChE: **492** (366 BBB+, 126 BBB-), down from 611.
Minimum detectable dAUC rises from 0.053 to **0.061**. BACE1: **89** (60/29), now
failing the sufficiency criterion on both the total and the minority class.

**Declined to move the primary cutoff to 0.3 despite better power** (1,066
compounds, MDE 0.041). Tanimoto 0.3 on Morgan fingerprints is a weak claim of
similarity, and buying power by loosening the definition of "in domain" would
undercut the paper's own argument. Recorded because the temptation was real and the
decision should be visible.

**Pre-registration amended to v1.1** with the fixed recipe, the new sample sizes,
the 0.061 power floor and the revised support threshold (dAUC >= 0.06). v1.0 was
never registered externally; both versions are in git history.

**No longer blocked.** The critical path is now external registration on OSF, then
the confirmatory analysis.

## 2026-11-16 — OSF submission package prepared

`docs/osf-submission.md`: paste-ready answers for every field of the OSF
Preregistration template, drawn from `docs/preregistration.md` v1.1.

**The "Existing data" answer is "Registration following analysis of the data."**
This is the honest answer and it will feel like the wrong one. The option covers
"calculation of descriptive statistics and observation of data distributions,"
which is exactly what the scoping, assay-metadata and sensitivity analyses did.
Claiming "before analysis" would be a misrepresentation, and a trivially detectable
one once the repository is public and timestamped. The template's "Explanation of
existing data" field is designed for this case and is used to state precisely what
was and was not done: no model trained, no error measured, no proximal-versus-
matched comparison computed.

**Analyst blinding, functional equivalent.** The confirmatory analysis code will be
written and validated on label-permuted data before being run once on real labels,
so the pipeline is fixed before any real outcome is observable. Recorded in the
registration under Blinding.

**Two blanks must be filled at submission:** the repository URL and the git commit
hash being registered against. The repo currently has no remote.

**Next:** a public remote (needed for the registration to reference), then register,
then write the confirmatory pipeline.

## 2026-11-16 — Confirmatory pipeline written, label-permuted validation running

`scripts/confirmatory.py` implements pre-registration sections 6–9 for the primary
endpoint. Committed before being run, so the permuted validation is tied to a
specific commit hash.

**The real-label run is gated in code, not by intention.** `--mode real` exits
unless four conditions hold: a registration identifier is supplied; a permuted run
is on record; that run used ≥ 100 draws; and it returned a ΔAUC confidence interval
covering zero. The permuted manifest must also match the current commit, so editing
the pipeline re-locks it. The pre-registered blinding substitute is therefore
enforced by the script rather than asserted in prose.

The pre-specified decision rules from section 9 are evaluated by the script and
printed as a verdict. A verdict computed by frozen code cannot be selected after
the number is known.

### Implementation clarifications the pre-registration did not settle

Both were decided and recorded **before any real-label run**. Neither changes a
pre-registered quantity; each resolves an ambiguity in how section 8 is realised.

**IC-1 — what pool the random control is drawn from.** Section 8 says "a random set
of identical size and class balance" without saying whether proximal compounds may
be drawn. Taken literally: arm B draws from the whole labelled set, so roughly 12.6%
of each control holdout is itself proximal. That dilution biases arm B **toward the
null**, making it the conservative reading, and it is the one adopted. The realised
share is reported per run (13.8% in the smoke test). Arm C draws from the distal
pool only, since a propensity-matched control containing proximal compounds would
defeat its purpose.

**IC-2 — hyperparameter tuning across arms.** Section 7 requires tuning "within the
training partition only." Tuning independently inside all 401 training partitions is
computationally gratuitous, and per-arm tuning would make the arms differ in two
ways at once. Resolution: tune once by 3-fold CV inside the **proximal arm's**
training partition — exactly as section 7 specifies for the primary arm — and share
that configuration with every control arm. A configuration identical across arms
cannot generate a between-arm difference, which is the only thing the primary
endpoint measures. Stated in the manuscript rather than left implicit, because the
control arms' evaluation compounds are inside the pool the configuration was chosen
on; with a four-point grid this is a very low-capacity channel and it is shared, not
differential.

**Threshold and calibration.** The decision threshold is chosen by maximising MCC on
out-of-fold predictions within each arm's own training partition, never on its
evaluation set. Calibration is Platt (sigmoid), which is monotonic and therefore
cannot change AUC — only the secondary Brier and ECE figures.

### What the smoke test already confirms about the design

Two draws are not a result, but the matching diagnostics are structural and do not
depend on the labels:

- **The property confound is real and large.** Proximal versus distal standardised
  mean differences: cLogP and TPSA around ±0.4. Arm B inherits that imbalance
  (cLogP −0.39, TPSA +0.38); arm C removes it (all three within ±0.05). This is
  precisely why section 8 makes arm C govern the conclusion, and the diagnostic now
  demonstrates the arms behave as designed.
- Permuted arm AUCs land near 0.5 as they must.

**Running:** 200-draw permuted validation, ~3 h. Until it returns null, the real
run stays locked.

**Still the critical path:** external registration on OSF. The pipeline can be
finished and validated without it, but the real-label run should not happen before
the registration is timestamped.

## 2026-11-16 — Two pipeline corrections found by running the permuted validation

The label-permuted run is a substitute for analyst blinding, but it also works as
what it is: a test harness on a null dataset. It caught two things before any real
labels were touched, which is the whole point of running it first.

**IC-3 — the primary endpoint is computed on the raw forest score, not the
calibrated probability.** Platt scaling is monotonic in expectation, so the original
code treated it as unable to affect AUC. That holds when there is signal to
calibrate. With permuted labels the fitted slope can come out *negative*, which
inverts the ranking and reflects AUC about 0.5. The permuted run showed it directly:
the proximal arm scored **AUC 0.470 raw against 0.535 calibrated** — the two sit on
opposite sides of chance, from one model on one evaluation set.

With real labels the slope will be firmly positive and the two will agree, so this
changes no expected result. It is fixed anyway, because an endpoint that depends on
the sign of a nuisance parameter is not a safe endpoint, and because the permuted
validation itself would otherwise be reading an inverted number. Calibration still
produces Brier and ECE and still sets the decision threshold. Both AUCs are
reported; `auc_calibrated` is retained in the output so the two can be compared.

**IC-4 — the permutation is varied, not fixed.** The proximal arm has exactly one
evaluation set, so a single permutation gives it a single realisation, and the
resulting ΔAUC could sit away from zero by luck rather than bias. `--permute-seed`
repeats the check across permutations; the canonical seed-42 run is the one the gate
reads, and the others are written beside it.

**Performance, no methodological content.** `ArmModel` replaces
`CalibratedClassifierCV` plus a nested `cross_val_predict` with one 3-fold loop that
retains its held-out predictions: identical quantities, three forest fits per arm
instead of twelve. `n_jobs` is fixed at 6 rather than -1, because nested parallelism
drove load average past 20 on a 10-core machine and throughput collapsed. A draw
costs about 3 s where it had been 3.5 min under contention.

**On the 4-draw numbers, which are not results.** Arm C sat about 0.02 above chance
and arm A about 0.03 below it. Four draws cannot distinguish that from noise — the
draw-to-draw spread was smaller than the sampling error of a single evaluation set,
which is what overlapping training partitions produce. The 200-draw runs across four
permutations are what settle it, and the gate will not unlock unless they return a
ΔAUC interval covering zero.

## 2026-11-16 — A false alarm, and the real defect under it (IC-5)

The first four permuted runs returned ΔAUC **+0.051, +0.019, +0.050, +0.000** —
every one positive, mean +0.030, which is half the pre-registered support threshold.
Two of them reported a descriptive tail probability of 0.010 and 0.005 on data
containing no signal whatsoever. The proximal arm's AUC across those four runs was
0.4703, 0.4726, 0.4659, 0.4774: mean 0.472, standard deviation 0.005, where the
Hanley–McNeil standard deviation for this class split is 0.028. An AUC varying five
times less than it should, sitting consistently below chance, looks like a biased
harness.

**It was not biased. The four seeds landed low together by chance.**
`scripts/validate_harness.py` establishes this with two tests, both on permuted
labels, and `results/harness_validation.txt` records the output:

- **Model frozen, evaluation labels permuted, 2,000 reps:** mean **0.4998**, sd
  **0.0277**, against a Hanley–McNeil prediction of **0.0274**. The metric is
  centred and has exactly the expected spread.
- **Joint permutation across twelve seeds:** mean **0.4913**, sd **0.0257**, range
  0.4556–0.5318, **t = −1.17** versus 0.5. The arm is centred under the null.

Recorded rather than quietly deleted, because the wrong conclusion was reachable
from the first four runs and the correction cost nothing but twelve more fits.

### IC-5 — the "empirical p" was invalid and has been removed

The defect the false alarm exposed. The quantity was the share of control draws
falling at or below the proximal AUC, printed as "empirical p". It compares **one**
proximal AUC against the spread of control **draws** — but the control median has a
small standard error over 200 draws, while the proximal arm carries its own sampling
error of ~0.028, which dominates and which this quantity ignores entirely. Whenever
the proximal arm landed a standard deviation low by chance, nearly every control
draw exceeded it and the number collapsed toward zero. **It manufactures
significance out of noise**, and on permuted data it duly produced 0.010 and 0.005.

It is now reported as a labelled descriptive share with an explicit note that it is
not a test. The confidence interval — which pairs a stratified bootstrap of the
proximal AUC with the control draw distribution, carrying both variance sources —
covered zero in all four permuted runs, as a correct interval should. It is the only
inferential quantity the study reports.

Had this run on real labels first, a chance-low proximal arm would have produced a
headline "p = 0.005" that no reviewer could have caught from the manuscript, because
the quantity sounds reasonable and the code was not public at the point the number
would have been quoted. This is the clearest justification the project has for
validating on permuted labels before real ones.

### The gate now judges six permutations, not one

One permutation characterises one realisation of a single fixed evaluation set.
`--mode real` therefore requires **six** valid permuted runs on the same pipeline
hash and tests their **mean** ΔAUC against ±0.02, in addition to the canonical run's
interval covering zero.

**Consequence for the power statement, which is unchanged but now better founded.**
The proximal arm's irreducible AUC spread of ~0.026–0.028 comes from measuring on
492 fixed compounds, and it is the reason the pre-registered minimum detectable
ΔAUC is ~0.061. The simulation in `scripts/power.py` said 0.061; the permutation
spread says the same thing by a different route. Section 9's warning — that a null
must be reported as "no degradation larger than ~0.06 AUC" — is now supported
empirically rather than only by simulation.

**Running:** eight 200-draw permuted runs, which is two more than the gate requires.

## 2026-11-17 — Permuted validation complete; the real-label run is unlocked

Eight 200-draw permuted runs on pipeline `922efb8f8c28`, summarised in
`results/permuted_validation_summary.txt` (regenerate with
`scripts/summarise_permuted.py`).

| | value |
| --- | --- |
| mean ΔAUC under the null | **+0.0075** |
| sd across runs | 0.0317 |
| t vs zero | **+0.67** |
| signs | 5 positive, 3 negative |
| intervals covering zero | **8 / 8** |

The gate's conditions are met: eight runs against a required six, all on one
pipeline hash, mean within ±0.02, every interval covering zero. Verified by calling
`check_unlocked()` directly rather than by starting a real run, so the pipeline file
was not touched and the eight runs stay pinned to it.

**This closes IC-5 cleanly.** The four development seeds were all positive with a
mean of +0.030; across eight seeds the signs are mixed and the mean is +0.0075.
Individual runs still reach +0.0509 and −0.0286 by chance, because each one's ΔAUC
is dominated by a proximal arm measured on a single fixed set of 492 compounds.
That is the same ~0.027 spread that sets the study's 0.061 minimum detectable
effect. Any single permuted run was always going to look like something.

**Note for the manuscript.** The methods section should report the mean across
permutations rather than a single validation run, and should say why: one
permutation validates one realisation. This is a small point that would be easy to
get wrong in writing up and is the kind of thing a reviewer of a pre-registered
methods audit will check.

### Environment failure, and what it cost

Five of the first eight runs never executed a line of Python. The interpreter died
in `site.py` reading `env/pyvenv.cfg` with `TimeoutError: [Errno 60]`. Cause: the
machine's iCloud account is at **175 bytes of remaining quota** with Desktop &
Documents sync enabled, and this repository sits in `~/Documents`, so iCloud was
failing to sync 333 MB of virtual environment while the local disk sat at 99% full.
Reads against the synced venv stalled. The same contention inflated completed runs
to 1 h and 3 h 39 m against about 20 minutes of actual work.

**Fixed:** the virtual environment now lives at `~/.venvs/bbb-domain-alzheimers`
with `env/` as a symlink, so `./env/bin/python` still works as documented
everywhere and the repository presents 15 MB rather than 333 MB to the sync daemon.
`requirements.txt` reproduces it exactly; versions are unchanged.

**Outstanding, and not a code issue:** the disk is still near capacity and the repo
still sits inside a permanently failing iCloud sync queue. Moving the project out of
`~/Documents` would remove a recurring source of non-deterministic failure in a
project whose whole value is reproducibility.

**Next, and now the only blocker:** OSF registration. The pipeline is finished,
validated and locked; `--mode real` requires a registration identifier and will
refuse without one.

## 2026-11-19 — Amendment A1: Component 2 specified, design component added

`docs/preregistration.md` now carries an **Amendments** section with A1, appended
rather than edited, per section 12.

**A1.1 closes a real gap.** Section 11 promised "a shortlist of AChE-directed
candidate compounds" and never said where the candidates came from. Three sentences,
all of them about what would *not* be claimed. Ambiguity in a pre-registered
component is what a reviewer attacks first. The shortlist is now specified as
**selected** from the 2,391 curated actives — compounds with measured human AChE
activity — with the out-of-domain 58.3% discarded *before* any BBB prediction is
made. "Candidate" means candidate for brain penetration; activity is measured,
penetration is predicted, and the manuscript must keep those words apart.

**A1.2 adds novel structures, by enumeration rather than generation.** The
distinction is the whole reason this is defensible. A learned generator carries its
own applicability domain, unexamined — which would reproduce, inside this paper, the
exact error the paper documents. Instead: a fixed catalogue of single
medicinal-chemistry transformations applied to in-domain parents, so every structure
traces to one named parent and one named transformation, and the component is
reproducible from the repository.

The framing is what makes it on-thesis rather than bolted on. The audit says
target-directed chemistry sits outside the predictors' domain; the constructive form
of that finding is a design constraint — **can AChE-directed chemistry be proposed
that stays inside the domain, so the BBB prediction on it is defensible?** Filter 2
makes in-domain membership a construction requirement rather than an outcome.

**No activity prediction is applied, deliberately.** Ranking novel structures by a
QSAR activity model would mean applying a model to novel chemistry without auditing
that model's domain. Omitting it costs the component any claim to potency, and that
cost is stated rather than hidden: the only activity-related claim available is
shared scaffold with a compound of measured activity.

**The weakness is the content.** Requiring in-domain membership biases proposals
toward chemistry resembling B3DB, which is enriched in approved and CNS-active
drugs, and the transformations are not chosen to preserve AChE binding. The
component trades plausibility-of-activity for defensibility-of-prediction and cannot
evaluate that trade without activity data. Written into the amendment in those
words.

Both components are exploratory, carry no p-values, and leave the confirmatory
analysis in sections 6–9 untouched. The amendment was written after the exploratory
58.3% figure was known and before any selection or enumeration was run; it says so.

`docs/osf-submission.md` updated to match under Exploratory analyses, so the
registration text and the pre-registration do not drift.

**Next for this component:** implement the enumeration. Filter thresholds are fixed
in writing first, which is what keeps it credible — they cannot be tuned once it is
visible what survives them.

## 2026-11-19 — Authorship order fixed: first/second, not co-first

Shreyan Kancharla first author, Sam second. An earlier co-first arrangement with an
equal-contribution footnote is **not** adopted.

The reason is simply that the work is not equal. The question, pre-registration,
curation decisions, confirmatory pipeline and its validation, domain and error
analysis, design-proposal enumeration and manuscript sit with the first author; the
second author's contribution is physicochemical interpretation, synthetic
accessibility, target-chemistry literature context and the corresponding sections.
That is a substantial second-author contribution and it is not an equal one. An
equal-contribution footnote the division of labour does not support would misstate
the record on the paper itself.

Recorded in `docs/preregistration.md` in both the Authors line and section 13.

**Owed to Sam directly.** Co-first authorship was floated to him earlier, and
`docs/project-pitch.pdf` — the version he has seen — still describes that
arrangement along with a curation role he no longer holds. He should hear the change
in a conversation rather than find it on a draft. Both the change and the reason are
defensible; being told late is what would not be.

## 2026-11-19 — REGISTERED on OSF

The pre-registration was submitted to OSF Registries and timestamped **2026-11-19**,
registered against commit `134ab6065bb6cbc79000944e52837932f7fe7219`. Public, not
embargoed. Schema: OSF Preregistration. Contributors: Shreyan Kancharla, Samuel
Siyanbola. Licence CC BY 4.0.

**DOI `10.17605/OSF.IO/UQR62`** — <https://osf.io/uqr62>. Archiving completed and the
registration accepted at 23:24:29 on 2026-11-19.

Title as registered: *Applicability domain of blood–brain barrier predictors in
Alzheimer's target chemical space: a methods audit and domain-constrained design.*
Broader than the working title, to cover the Amendment A1 design component.

**The exploratory/confirmatory boundary is now closed.** Everything computed before
this date is exploratory and must be labelled so in the manuscript. The confirmatory
analysis has not been run.

OSF's newer schema differs from the one `docs/osf-submission.md` was written
against: the old three-option "Existing data" question is replaced by an eight-level
"Foreknowledge of data or evidence" scale. The selected level was **"Authors have
observed the data, but have not performed the proposed analyses"** — which describes
this study exactly, where the old form forced a blunter answer. `docs/osf-submission.md`
should be rewritten against the newer schema so the repository records what was
actually registered rather than a form that no longer exists.

Material added at registration that is not in `docs/preregistration.md` and should
be carried into the manuscript's methods:

- **Negative control**, stated as a pre-registered precondition: the pipeline run on
  label-permuted data, eight permutations, mean ΔAUC +0.0075 (sd 0.0317, t = +0.67),
  all eight intervals covering zero.
- **Manipulation check** with a failure rule: property matching verified by
  standardised mean differences, target |SMD| < 0.1 on MW, cLogP and TPSA. If the
  property-matched arm misses that on any covariate, the matching is reported as
  failed and the primary comparison reported as confounded rather than quietly
  accepted.
- **Assumption handling**: the primary endpoint is rank-based and distribution-free;
  the bootstrap is stratified by class; non-convergence of the propensity model
  within 2,000 iterations would be treated as matching failure.

**Next:** retrieve the DOI, record it here and in the pre-registration, then run
`scripts/confirmatory.py --mode real --registered <DOI>`. The gate will refuse
without it.
