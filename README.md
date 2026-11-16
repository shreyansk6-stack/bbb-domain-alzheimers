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
(`docs/literature-search.md`). Pre-registration not yet written, and is the next step.

See `docs/decisions.md` for the dated log.

## Headline scoping result

Share of target actives with no B3DB neighbour above the given Tanimoto cutoff
(Morgan fingerprints, radius 2, 2048 bits):

| Target | n | <0.3 | <0.35 | <0.4 | median |
| --- | --- | --- | --- | --- | --- |
| BACE1 | 7,481 | 85.8% | 97.2% | 99.4% | 0.252 |
| Acetylcholinesterase | 3,125 | 26.4% | 53.9% | 71.9% | 0.343 |

BACE1 inhibitors sit almost entirely outside the chemistry B3DB covers.
Acetylcholinesterase inhibitors are reasonably well covered. The contrast is the
backbone of the planned paper: AChE serves as a positive control, and BACE1 as the
case where no public ground truth exists to validate the filter against.

**These numbers are exploratory.** They were computed before any pre-registration and
must be reported as such. The modelling and error analysis has not been run.

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

`fetch_chembl.py` pulls BACE1 (CHEMBL4822) and acetylcholinesterase (CHEMBL220),
both human, filtering to IC50/Ki with pChEMBL ≥ 6. That activity threshold is a
placeholder pending a chemistry decision — see `docs/decisions.md`.

## Known risks

- **Distance may not predict error.** Comput Biol Chem 2026
  (10.1016/j.compbiolchem.2026.109356) found a 0.32-0.39 AUC generalisation gap while
  its applicability-domain analysis showed complete structural coverage, concluding
  out-of-domain extrapolation did not explain the gap. The design must measure error
  directly, not infer it from distance.
- **No BACE1 ground truth.** Only 145 B3DB compounds fall within 0.35 of BACE1
  chemistry, 49 within 0.4. Error cannot be measured there; the absence is itself
  the finding.
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
docs/      decision log, pre-registration (when written)
```
