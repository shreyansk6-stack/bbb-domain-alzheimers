# Applicability domain of blood–brain barrier predictors in Alzheimer's target space

Are the blood–brain barrier (BBB) predictions used routinely in Alzheimer's
virtual-screening pipelines valid for the compounds they are actually applied to?

Alzheimer's screening papers commonly rank compounds for activity against a target
(BACE1, acetylcholinesterase), then filter the hits through an off-the-shelf BBB
predictor to ask whether a compound can reach the brain. BBB predictors are trained
on literature-derived datasets that skew toward approved and CNS-active drugs. Target
inhibitor series are narrow, heavily optimised medicinal chemistry. This project
measures the gap between those two chemical spaces and what it costs in prediction
error.

## Status

**Registered and analysed.** Pre-registration `docs/preregistration.md` was
registered on OSF on 2026-11-19, DOI
[`10.17605/OSF.IO/UQR62`](https://doi.org/10.17605/OSF.IO/UQR62), against commit
`134ab60`. `docs/osf-submission.md` is the field-by-field record of what was
submitted.

**The confirmatory analysis is complete and closed.** One run, real labels,
2026-11-20. Verdict **INCONCLUSIVE**, computed by the frozen script from the
pre-specified rules.

| Comparison | ΔAUC | 95% CI |
| --- | --- | --- |
| **vs property-matched control (governs)** | **+0.0284** | **[−0.0164, +0.0749]** |
| vs unmatched random control | +0.0553 | [+0.0071, +0.1005] |

Must be reported as "no degradation larger than ~0.06 AUC", never as no
degradation: the minimum detectable effect is 0.061 and the point estimate is
0.028.

The substantive finding is the gap between those two rows. **About 49% of the
apparent degradation is molecular-property difference rather than domain novelty** —
pre-registered in section 8 as the quantity to report if the arms disagreed. A study
using an unmatched control would have reported a significant effect, half of it
confounded.

Calibration degrades out of domain while discrimination barely does: ECE 0.0971 vs
0.0601, Brier 0.1449 vs 0.1283. Secondary, no decision rule, no p-value.

**Do not re-run `scripts/confirmatory.py`, and do not edit it.** Section 9 forbids
resolving an inconclusive result by adding metrics, cutoffs, models or targets. The
script is hash-gated and any edit re-locks it. Full output in
`results/confirmatory_real.txt`.

Open work: the exploratory components of Amendment A1 (in-domain shortlist; A1.2
design enumeration), the pre-registered secondary analyses, and the manuscript.
New contributors start at `docs/onboarding-sam.md`.

See `docs/decisions.md` for the dated log.

## Headline scoping result

Share of target actives with no B3DB neighbour above the given Tanimoto cutoff
(Morgan fingerprints, radius 2, 2048 bits), under the primary curation recipe
(`docs/curation-decisions.md`):

| Target | n | <0.3 | <0.35 | <0.4 | median |
| --- | --- | --- | --- | --- | --- |
| BACE1 | 5,157 | 85.8% | 97.5% | 99.4% | 0.252 |
| Acetylcholinesterase | 2,391 | 28.4% | 58.3% | 77.2% | 0.333 |

BACE1 inhibitors sit almost entirely outside the chemistry B3DB covers.
Acetylcholinesterase inhibitors are reasonably well covered. The contrast is the
backbone of the planned paper: AChE serves as a positive control, and BACE1 as the
case where no public ground truth exists to validate the filter against.

For context, published BBB models report ~94% of their *own test compounds* as
in-domain. That figure is near-guaranteed by construction; the table above is the
same measurement taken against the chemistry such models are deployed on.

**These numbers are exploratory.** They were computed before any pre-registration and
must be reported as such. The modelling and error analysis has not been run.

### The result survives every curation choice

Ten curation variants — pooling IC50 with Ki or not, confidence score 8 versus 9,
activity thresholds from pChEMBL 5 to 8, assay types, deduplication — move BACE1
within 81.8–89.4% and AChE within 21.7–36.4% at the 0.3 cutoff. The worst case for
the contrast still leaves a 45-point gap. Full table in `results/sensitivity.txt`
and `docs/curation-decisions.md`.

That matters because the two standard references on ChEMBL curation disagree about
pooling IC50 with Ki (`10.1371/journal.pone.0061007` permits it with an offset;
`10.1021/acs.jcim.4c00049` warns against it). We measured the disagreement in our
own data — 46.9% of replicated BACE1 compounds span more than 0.3 log units — and
it does not reach our conclusion, because the activity threshold decides only set
membership and no potency value enters any model.

### Feasibility gate

Labelled B3DB compounds near target chemistry, which is what error can be measured
on. Pre-registered criterion: ≥200 compounds with ≥50 in each class at 0.35.

| Target | within 0.35 | BBB+ / BBB− | gate | min. detectable ΔAUC |
| --- | --- | --- | --- | --- |
| Acetylcholinesterase | 492 | 366 / 126 | passes | 0.061 |
| BACE1 | 89 | 60 / 29 | **fails** | 0.136 |

BACE1 error is therefore not measurable with existing public data, which is itself
a primary finding rather than a limitation.

## Data

Neither dataset is committed; `data/` is gitignored, because ChEMBL is CC BY-SA and
share-alike would propagate to this repository.

> **Do not refetch the data to obtain a working copy.** ChEMBL is a live API and
> ChEMBL_38 would differ from the registered ChEMBL_37 snapshot. The pre-registration
> forbids refetching without a dated amendment. Get `data/` by direct transfer from a
> collaborator and verify it with
> `shasum -a 256 -c docs/data-manifest.sha256`, which pins the exact registered
> snapshot. The fetch commands below are kept as a record of how the snapshot was
> built, not as setup instructions.

| Source | Version used | Licence | Notes |
| --- | --- | --- | --- |
| [B3DB](https://github.com/theochem/B3DB) | main, fetched 2026-11-14 | CC0 1.0 | Cite Meng et al., *Scientific Data* 2021 |
| [ChEMBL](https://www.ebi.ac.uk/chembl/) | ChEMBL_37 (released 2026-05-01) | CC BY-SA 3.0 | Share-alike: derived datasets carry the same licence |

ChEMBL is a live API and releases change. Record the release in `docs/decisions.md`
whenever the data is refetched.

## Reproducing the scoping check

```sh
python3 -m venv env
./env/bin/pip install rdkit pandas
mkdir -p data results

curl -sL -o data/B3DB_classification.tsv \
  https://raw.githubusercontent.com/theochem/B3DB/main/B3DB/B3DB_classification.tsv
curl -sL -o data/B3DB_regression.tsv \
  https://raw.githubusercontent.com/theochem/B3DB/main/B3DB/B3DB_regression.tsv

./env/bin/python -I scripts/fetch_chembl.py data/chembl_actives.json
./env/bin/python -I scripts/gate.py data | tee results/scoping_overlap.txt
```

`probe_chembl.py` is the current fetch step: it pulls activities at a deliberately
loose threshold together with their assay metadata, caching them to
`data/chembl_probe.json` so curation recipes can be re-applied without refetching.
`sensitivity.py` then applies the primary recipe and every contested variant.

```sh
./env/bin/python -I scripts/probe_chembl.py data/chembl_probe.json
./env/bin/python -I scripts/sensitivity.py  data | tee results/sensitivity.txt
./env/bin/python -I scripts/curate_gate.py  data | tee results/curated_overlap.txt
./env/bin/python -I scripts/power.py             | tee results/power.txt
```

`fetch_chembl.py` and `gate.py` are the original scoping scripts, kept because
`results/scoping_overlap.txt` came from them. They apply no assay-quality filters
and are superseded by the two scripts above.

## Known risks

- **Distance may not predict error.** Comput Biol Chem 2026
  (10.1016/j.compbiolchem.2026.109356) found a 0.32-0.39 AUC generalisation gap while
  its applicability-domain analysis showed complete structural coverage, concluding
  out-of-domain extrapolation did not explain the gap. The design must measure error
  directly, not infer it from distance.
- **No BACE1 ground truth.** After curation only 101 B3DB compounds fall within 0.35
  of BACE1 chemistry, 28 within 0.4. Error cannot be measured there; the absence is
  itself the finding.
- **The AChE positive control is tighter than it looked.** Curation cuts usable
  in-domain ground truth from 942 to 611 compounds at 0.35 (464 BBB+, 182 BBB-).
  Still workable, but the error-measurement design must be powered for ~600, not
  ~950, and class imbalance handled explicitly.
- **Threshold sensitivity.** Out-of-domain fractions move substantially with the
  cutoff. Pre-register the criterion and report the full sweep.
- **Label quality.** B3DB is compiled from ~50 heterogeneous sources.
- **Label quality, sharpened.** Deduplicating B3DB on canonical SMILES finds only 3
  duplicates; deduplicating on InChIKey skeleton collapses it to 3,952 compounds and
  exposes 131 skeletons with discordant BBB+/BBB- labels (preprint
  10.20944/preprints202609.2002.v1). Curation must work at the skeleton level, and
  the scoping numbers below pre-date this and need recomputing.
- **Possible scoop: closed.** A systematic Europe PMC search on 2026-11-16 found the
  specific question unclaimed; zero hits for BBB + applicability domain in title and
  for BBB + chemical space + coverage. Record in `docs/literature-search.md`.

## Layout

```
scripts/   analysis code
data/      gitignored; fetched by the commands above
results/   captured script output
docs/      decision log, literature search, pre-registration
```
