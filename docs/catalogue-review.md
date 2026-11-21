# Chemistry review — answers

**Reviewed 2026-11-21.** The co-author declined to answer and asked that the
questions be settled from the literature, with reasoning where the literature is
silent.

> **This review was not performed by a practising medicinal chemist.** It is
> literature-grounded reasoning, not bench judgement. The manuscript's limitations
> section must say so, and the author-contributions statement must not claim
> medicinal-chemistry review that did not occur. See "Consequences for the
> manuscript" at the end.

---

## Q1. The catalogue

| id | transformation | verdict | survivors |
| --- | --- | --- | --- |
| T01 | acid → tetrazole | **reject** | 0 |
| T02 | acid → primary amide | approve, with note | 0 |
| T03 | methyl ester → primary amide | approve | 0 |
| T04 | benzene → pyridine | **approve — highest value** | 0 (blocked) |
| T05 | aromatic fluorine scan | approve | 471 |
| T06 | aromatic chlorination | approve | 267 |
| T07 | methyl → ethyl | approve, low information | 11 |
| T08 | N-demethylation | approve, with caveat | 44 |
| T09 | morpholine → piperidine | approve | 0 (blocked) |
| T10 | piperidine → morpholine | **reclassify as diagnostic** | 0 (blocked) |

**T01 — reject.** Tetrazole is the canonical carboxylic acid bioisostere and is
correct in general (Ballatore et al., *ChemMedChem* 2013), but it is the wrong move
for *this* objective. Tetrazole's pKa (~4.9) is close to a carboxylic acid's, so it
remains anionic at physiological pH and the permanent negative charge that obstructs
passive diffusion is retained. It buys lipophilicity, not brain exposure. A catalogue
aimed at CNS exposure should not contain it. **Consequence: the F6 block on T01 costs
nothing.**

**T02 — approve, with note.** Removing the ionisable centre entirely is the right
move where the acid is not required for binding. Note that a primary amide *raises*
TPSA slightly (37.3 → 43.1 Å²) and adds two hydrogen-bond donors, and HBD count is
among the strongest determinants of CNS exposure (Wager et al., *ACS Chem Neurosci*
2010). A **secondary (N-methyl) amide would be the better CNS choice** and is the
version to use if the catalogue is ever revised.

**T03 — approve.** Replacing a metabolically labile methyl ester with an amide is
standard and uncontroversial. Same HBD caveat as T02.

**T04 — approve, and this is the most valuable entry in the catalogue.** Substituting
an aromatic CH for N lowers logP by roughly one unit, adds an acceptor, improves
solubility and frequently reduces hERG liability. It is the standard first move
against excessive lipophilicity in CNS programmes (Pennington & Moustakas, *J Med
Chem* 2017). **Consequence: the F6 block on T04 does cost real chemistry — see Q2a.**

**T05 — approve.** Aromatic fluorination blocks metabolic oxidation at the position
and raises lipophilicity only modestly (π ≈ 0.14). Ubiquitous in CNS medicinal
chemistry. See Q3a for what it is worth *as a proposal*.

**T06 — approve.** My initial instinct was to reject this on the grounds that
chlorine raises lipophilicity substantially (π ≈ 0.71) and these parents already
average cLogP 3.28. That instinct was wrong: aryl chloride is extremely common in
marketed CNS drugs (chlorpromazine, clozapine, haloperidol), and the cLogP ≤ 4
property filter already removes the products where the increase would matter. The
entry stands.

**T07 — approve, low information.** A single-carbon homologation is a legitimate SAR
probe. It tells you little without assay feedback, and it contributes 11 compounds.
Harmless.

**T08 — approve, with caveat.** N-demethylation lowers logP and MW, which is the
right direction, but it converts a tertiary to a secondary amine and so **adds an
HBD**, which is the wrong direction for CNS. It is also a common *metabolic* route,
so the product is frequently a known metabolite rather than a novel design. Keep, but
it is the weakest of the four that produced output.

**T09 — approve.** Removing the morpholine oxygen raises logP and basicity and lowers
TPSA. Where a morpholine has made a series too polar to cross, this is the standard
correction.

**T10 — reclassify.** Morpholine→piperidine and piperidine→morpholine cannot both be
proposed as improvements; as design moves they are contradictory. T10 was included
deliberately as a check on whether the model rates both directions as improvements,
which would show it is not tracking anything physical. That is a **model diagnostic,
not a design proposal**, and should be labelled as such rather than carried in a
catalogue of proposals.

### Q1b. What is missing

**The catalogue has no HBD-reducing transformation, and that is its largest gap.**
After TPSA, hydrogen-bond donor count is the strongest simple determinant of CNS
exposure. The obvious entry — **N-methylation of a secondary amide** — is absent,
and it is the inverse of T08, which is present. Also absent: ring saturation to raise
Fsp3, and any edit targeting P-gp efflux liability, for which TPSA and HBD are only
proxies.

This is a genuine weakness in A1.2 as registered and should be stated in the paper.

---

## Q2. The four transformations F6 blocks

**Q2a. Benzene → pyridine: yes, this is a real loss.** It is the highest-value entry
in the catalogue, and the scaffold-retention filter rejects all 1,242 of its products
before chemistry is considered. **The 86-compound figure understates the cost in
quality terms**: 62 of those 86 are the N-walk, and they are chemically more
interesting than the 793 that survived. The manuscript should say this rather than
leaning on the raw count to make the defect sound minor.

**Q2b. T09 yes, T10 as a diagnostic only** (see above).

**Q2c. T01 no** — rejected on CNS grounds independently, so its block costs nothing.

Net: of the four blocked transformations, **one (T04) represents a substantive loss,
one (T09) a modest one, and two (T01, T10) no loss at all.**

---

## Q3. 93% halogen scans

**Q3a. Describe it more modestly.** Fluorine and chlorine scanning are real
medicinal chemistry, but they are *optimisation* moves made iteratively against assay
feedback, not hypothesis-generating design. Proposed cold, with no activity data and
no assay loop, a halogen scan is a minimal perturbation rather than a design
hypothesis.

The honest framing for the paper: these are **compounds that demonstrate the
constraint** — the smallest edits that keep a molecule inside the predictor's domain
— not a drug-design contribution. The component's value is in showing what
domain-constrained enumeration yields, and that what it mostly yields is minimal
perturbation. That is a legitimate and mildly deflating result, and it should be
reported as one.

**Q3b. Chlorination is fine** — see T06 above. My initial concern was wrong.

---

## Q4. Curation criteria — all three agreed

**Q4a. pChEMBL ≥ 6 — agree.** 1 µM is a conventional activity cutoff for
ChEMBL-derived target sets, and slightly permissive for AChE, where reference
inhibitors reach low nM. Permissive is correct here: the set defines *chemical space
occupied by compounds made against this target*, not a potency-ranked series. Potency
never enters any model.

**Q4b. IC50/Ki pooled, Kd excluded, median aggregation — agree.** Pooling introduces
roughly 0.5 log of additional error (Kalliokoski et al. 2013; Landrum & Riniker
2024), which would matter for a potency model and does not matter here, because the
threshold decides only set membership. The ten-variant sensitivity analysis confirms
it empirically: the out-of-domain contrast holds in every variant.

**Q4c. Confidence score 9 only — agree, and this is the right call.** *Torpedo
californica* and *Electrophorus electricus* AChE differ from the human enzyme in
gorge-lining residues, and inhibitor SAR transfers poorly between them. Pooling them
would contaminate the definition of "AChE chemical space" with chemistry optimised
against a different protein. Excluding them costs set size and buys correctness.

---

## Q5. The property window

**Q5a. MW ≤ 450, cLogP 1–4, TPSA ≤ 90 is defensible but incomplete.** It aligns with
conventional CNS guidance (Pajouhesh & Lenz 2005; Wager's CNS MPO, which prefers
MW ≤ 360 and cLogP ≤ 3 — our window is looser on both). **The omission is HBD**,
which CNS MPO weights heavily.

Checked empirically rather than assumed: HBD across the reported 20 is 0 in six
compounds, 1 in thirteen, 2 in one. **The omission did not bite** — the surviving
compounds are CNS-appropriate on HBD anyway. Report HBD as a column (now done) and
note the filter's absence as a limitation. Do not add the filter now; that would be a
post hoc change made after seeing it was unnecessary.

**Q5b. Keep the cLogP ≥ 1 bound.** A lower bound is justified — very polar compounds
do not cross passively — and 1 is a conventional if arbitrary choice. It is what
removes the T02/T03 amide products. Removing it now to recover compounds would be
loosening a filter after seeing what it excluded, which is precisely the move this
project has refused three times already. Keep it and report the consequence.

---

## Q6. The top 20

**Q6a. One genuine problem, found by inspection and confirmed by a structural-alert
scan.**

**Compound #10 is an aryl thiosulfonate** (`CCc1ccc(S(=O)(=O)SCc2ccccc2)cc1`). That
is a thiol-reactive electrophile — the chemotype is used deliberately as a
cysteine-modifying reagent. It should not be proposed as a design candidate without a
reactivity flag. **PAINS does not catch it**, which is a useful demonstration that
PAINS alone is insufficient screening hygiene.

A BRENK alert scan over all 793 survivors was therefore run:

| catalogue | flagged |
| --- | --- |
| PAINS (filter F8, already applied) | 0 / 793 |
| NIH | 4 / 793 |
| **BRENK** | **200 / 793** |

Leading BRENK alerts: aliphatic long chain (61), Michael acceptor (24), nitro group
(21), aldehyde (17), diketo (14). **Seven of the reported 20 carry an alert.**

These liabilities are **inherited from the parent compounds** — real ChEMBL AChE
actives — not created by our single edits. That is an important distinction and it is
not a defence: a proposal list should surface them.

**Action taken: flagged, not removed.** `results/design_proposals.{txt,csv}` now carry
a BRENK alert column and an HBD column, and the table states that 7 of 20 are
flagged. Removing them would be adding a filter after seeing the output, which is the
move being refused elsewhere in this project. A reader sees the flag and judges.

**Q6b. Report the Amendment A2 table in the main text**, with the Tanimoto column
prominent and the depth-in-domain tradeoff stated, and put the original-rule table in
supplementary. Twenty distinct scaffolds demonstrate the method; six scaffolds of
positional isomers do not. The counter-argument — that the A2 set sits at Tanimoto
0.35–0.48, near the domain boundary — is real and is why the column must be visible.

---

## Q7. Editorial

**Q7a. Move the design component to supplementary**, with a short main-text paragraph
pointing to it.

The paper's strength is the audit. The design component is exploratory, claims
nothing about activity, has three documented internal defects, and — per Q3a — mostly
produces minimal perturbations. Presenting it as a co-equal contribution invites a
reviewer to attack the weakest part of the paper and makes the stronger findings look
like scaffolding for a compound list. A short main-text paragraph plus full
supplementary treatment gets the demonstration without the exposure.

**Q7b. The author-contributions statement must be rewritten.** The current draft
claims medicinal-chemistry judgement on curation and catalogue that this review
replaced. See below.

---

## Consequences for the manuscript

1. **Limitations must state that the transformation catalogue and curation criteria
   were not independently reviewed by a practising medicinal chemist**, and that the
   assessment above is literature-grounded reasoning.
2. **The author-contributions statement must match what happened.** It cannot claim
   medicinal-chemistry review that did not take place. The wording is for the authors
   to settle.
3. **§3.9 moves to supplementary**, with a main-text paragraph.
4. **The design component's framing changes** from "proposed structures" to
   "compounds demonstrating the domain constraint", per Q3a.
5. **The F6 defect is reported as a quality loss, not only a count loss** — the
   aromatic N-walk is the catalogue's best entry and it was blocked entirely.
6. **The missing HBD transformation** is added to the catalogue's stated weaknesses.
7. **The BRENK finding is reported**: 200 of 793 survivors and 7 of 20 reported
   compounds carry structural alerts inherited from their parents, and PAINS alone
   catches none of them.
