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

Scoping complete. Literature search complete — the question is confirmed unclaimed
(`docs/literature-search.md`). **Pre-registration written**
(`docs/preregistration.md`, v1.0, 2026-11-16) and awaiting the chemistry
co-author's sign-off on the activity threshold.

No model has been trained and no error has been measured. The next step is the
confirmatory analysis in section 8 of the pre-registration.

See `docs/decisions.md` for the dated log.

## Headline scoping result

Share of target actives with no B3DB neighbour above the given Tanimoto cutoff
(Morgan fingerprints, radius 2, 2048 bits), after InChIKey-skeleton curation of
both sides:

| Target | n | <0.3 | <0.35 | <0.4 | median |
| --- | --- | --- | --- | --- | --- |
| BACE1 | 6,918 | 86.0% | 97.2% | 99.3% | 0.250 |
| Acetylcholinesterase | 3,014 | 26.8% | 54.7% | 72.8% | 0.342 |

BACE1 inhibitors sit almost entirely outside the chemistry B3DB covers.
Acetylcholinesterase inhibitors are reasonably well covered. The contrast is the
backbone of the planned paper: AChE serves as a positive control, and BACE1 as the
case where no public ground truth exists to validate the filter against.

For context, published BBB models report ~94% of their *own test compounds* as
in-domain. That figure is near-guaranteed by construction; the table above is the
same measurement taken against the chemistry such models are deployed on.

**These numbers are exploratory.** They were computed before any pre-registration and
must be reported as such. The modelling and error analysis has not been run.

### Curation effect

Skeleton-level deduplication barely moves the headline (BACE1 85.8% to 86.0% at
0.3; AChE 26.4% to 26.8%) but cuts the available ground truth by about a third,
because the labelled data nearest to target chemistry is disproportionately
stereoisomer-redundant:

| | raw | curated |
| --- | --- | --- |
| B3DB records / skeletons | 7,805 | 4,022 |
| labelled reference set (discordant removed) | 7,805 | 3,892 |
| B3DB compounds within 0.35 of AChE | 942 | 611 |
| B3DB compounds within 0.35 of BACE1 | 145 | 101 |

Curation independently reproduces the published counts it was derived from
(4,022 vs 3,952 skeletons; 130 vs 131 discordant labels), which is a useful check
on the pipeline.

## Data

Neither dataset is committed; `data/` is gitignored. Reproduce with the scripts below.

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

`curate_gate.py` applies InChIKey-skeleton deduplication and recomputes the same
quantities; `results/curated_overlap.txt` is its output and supersedes
`scoping_overlap.txt`, which is kept for comparison.

```sh
./env/bin/python -I scripts/curate_gate.py data | tee results/curated_overlap.txt
./env/bin/python -I scripts/power.py            | tee results/power.txt
```

`fetch_chembl.py` pulls BACE1 (CHEMBL4822) and acetylcholinesterase (CHEMBL220),
both human, filtering to IC50/Ki with pChEMBL ≥ 6. That activity threshold is a
placeholder pending a chemistry decision — see `docs/decisions.md`.

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
