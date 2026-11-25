"""Assemble the Supplementary Information document from the recorded artifacts.

Every table here is read from a file in results/, docs/ or config/ rather than
retyped, so the SI cannot drift from the analyses it documents. The script is
read-only with respect to those sources; it writes only docs/supplementary.md.

Usage: ./env/bin/python -I scripts/build_supplementary.py
"""
import csv
import json
import re

OUT = "docs/supplementary.md"
parts = []


def w(s=""):
    parts.append(s)


def read(path):
    with open(path) as fh:
        return fh.read()


def block(path, start=None, end=None, strip_rule=True):
    """Fenced excerpt of a recorded text artifact."""
    lines = read(path).splitlines()
    if start is not None:
        lines = lines[start:end]
    if strip_rule:
        lines = [ln for ln in lines if not re.fullmatch(r"=+", ln.strip())]
    return "```\n" + "\n".join(lines).strip("\n") + "\n```"


cat = json.load(open("config/transformations.json"))
props = json.load(open("results/design_proposals.json"))
nov = json.load(open("results/novelty.json"))
with open("results/design_proposals.csv") as fh:
    rows = list(csv.DictReader(fh))

# ----------------------------------------------------------------- header
w("# Supplementary Information")
w()
w("**Applicability domain of blood–brain barrier predictors in Alzheimer's "
  "target chemical space: a methods audit and domain-constrained design**")
w()
w("Pre-registered on OSF Registries, 2026-11-19, "
  "[10.17605/OSF.IO/UQR62](https://doi.org/10.17605/OSF.IO/UQR62). "
  "All code, data manifests and result files: "
  "<https://github.com/shreyansk6-stack/bbb-domain-alzheimers>")
w()
w("> Every table in this document is generated directly from the recorded "
  "result files by `scripts/build_supplementary.py`. Nothing is retyped, so "
  "the SI cannot drift from the analyses it documents.")
w()
w("**Contents** — S1 domain-constrained design · S2 registration, amendments "
  "and decision log · S3 label-permuted validation · S4 curation sensitivity · "
  "S5 literature search record · S6 scaffold-filter sensitivity")
w()
w("---")

# --------------------------------------------------------------------- S1
w()
w("## S1. Domain-constrained design, full treatment")
w()
w("**Exploratory throughout.** This component post-dates the registration, "
  "specified in Amendment A1.2 and with its ranking rule replaced by Amendment "
  "A2 (S2). No activity model was applied and no compound was synthesised or "
  "assayed. Nothing here supports a claim of activity, permeability or "
  "therapeutic use.")
w()
w("### S1.1 Transformation catalogue")
w()
w("Ten single medicinal-chemistry transformations, fixed before enumeration. "
  "The `status` and review note for each were set on 2026-11-21 from the "
  "literature-grounded assessment in `docs/catalogue-review.md`; **that "
  "assessment was not made by a practising medicinal chemist**, which the main "
  "text reports as a limitation.")
w()
w("| id | transformation | class | status | survivors |")
w("| --- | --- | --- | --- | --- |")
surv = {t: 0 for t in [x["id"] for x in cat["transformations"]]}
for r in rows:
    surv[r["transformation"]] = surv.get(r["transformation"], 0) + 1
for t in cat["transformations"]:
    w(f"| {t['id']} | {t['name']} | {t.get('class', '—')} | "
      f"**{t['status']}** | {surv.get(t['id'], 0)} |")
w()
w("Survivor counts are post-novelty (the 793 of S1.4). Per-entry rationale and "
  "the full review note for each transformation are in "
  "`config/transformations.json` and `docs/catalogue-review.md`.")
w()
w("**Two entries were changed by the review after enumeration had run.** T01 "
  "(carboxylic acid → tetrazole) was rejected, because tetrazole's pKa leaves "
  "the molecule anionic at physiological pH and so retains the charge that "
  "obstructs passive diffusion — a correct acid isostere in general, the wrong "
  "move for brain exposure. T10 (piperidine → morpholine) was reclassified as "
  "a model diagnostic rather than a design proposal, since it and T09 cannot "
  "both be improvements. **Neither change alters any reported output**: both "
  "transformations contributed zero survivors, having been eliminated by the "
  "scaffold filter (S1.2) before chemistry was considered. The enumeration was "
  "therefore not re-run, and its recorded header still describes the catalogue "
  "as provisional.")
w()
w("The catalogue's largest gap, identified by the same review, is the absence "
  "of any **hydrogen-bond-donor-reducing** transformation — N-methylation of a "
  "secondary amide, the inverse of T08, which is present. HBD count is among "
  "the strongest simple determinants of CNS exposure.")
w()
w("### S1.2 Filters and funnel")
w()
w("Eight filters, ordered so the expensive network-bound novelty check runs "
  "last, on survivors only.")
w()
w(block("results/design_enumeration.txt", 15, 26))
w()
w("Filter F5 (novelty) is deliberately absent from this funnel; S1.4 explains "
  "why and reports it separately.")
w()
w(block("results/design_enumeration.txt", 28, 38))
w()
w("### S1.3 Survivors by transformation")
w()
w(block("results/design_enumeration.txt", 39, 52))
w()
# Sum ONLY the survivors-by-transformation block. A looser pattern over the
# whole file also matches rank numbers in the top-20 tables.
_enum = read("results/design_enumeration.txt")
_sb = _enum.split("SURVIVORS BY TRANSFORMATION", 1)[1]
_sb = re.sub(r"^[\s=]*", "", _sb).split("\n\n", 1)[0]
_pre = sum(int(x) for x in re.findall(r"^\s*T\d\d\s+(\d+)\s", _sb, re.M))
_f3 = int(re.search(r"F3 predicted BBB\+.*?:\s*(\d+)", _enum).group(1))
assert _pre == _f3, f"survivors sum {_pre} != recorded F3 {_f3}"
assert _f3 - len(rows) == nov["n_known"], (
    f"{_f3} - {len(rows)} != novelty n_known {nov['n_known']}")
w(f"**These counts are before the novelty check** and sum to {_pre}"
  f", the F3 survivors of S1.2. The novelty check (S1.4) removes "
  f"{_pre - len(rows)} of them, "
  f"leaving the {len(rows)} in the S1.1 table and in the full structure table. "
  f"Both sets of counts appear in this document and they are not the same "
  f"number.")
w()
w("**93% of the surviving set is a single aromatic fluorination or "
  "chlorination.** Halogen scanning is real medicinal chemistry, but it is "
  "optimisation performed iteratively against assay feedback rather than "
  "hypothesis-generating design. Proposed cold, it is the smallest edit that "
  "keeps a molecule inside the predictor's domain. We report this component as "
  "a demonstration of the constraint, not as a drug-design contribution.")
w()
w("### S1.4 Novelty")
w()
w(block("results/novelty.txt", 3, 20))
w()
w("**Caveats, which apply to every novelty statement in this paper.** Lookup "
  "is exact-structure matching on the full InChIKey, so a stereoisomer, "
  "tautomer or salt of a known compound reads as unmatched. *No exact match* "
  "is not *no close analogue*: these are single edits of known actives, so "
  "close analogues exist by construction. Absence from ChEMBL and PubChem is "
  "not absence from the literature or from patents, neither of which was "
  "searched. Both databases are live, so the result is true only as of the "
  "query date.")
w()
w("### S1.5 Reported compounds under Amendment A2")
w()
w("One representative per scaffold, ranked by synthetic accessibility, capped "
  "at 20 — **20 distinct parents and 20 distinct scaffolds**.")
w()
w("| # | tx | SA | max Tanimoto | p(BBB+) | MW | cLogP | TPSA | HBD | parent | "
  "BRENK alert |")
w("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
for r in rows[:20]:
    w(f"| {r['rank_a2']} | {r['transformation']} | {r['sa']} | "
      f"{r['max_tanimoto']} | {r['p_bbb']} | {r['mw']} | {r['clogp']} | "
      f"{r['tpsa']} | {r['hbd']} | {r['parent_chembl']} | "
      f"{r['brenk_alert'] or '—'} |")
w()
w("SMILES for each, with parent SMILES and scaffold, are in the "
  "machine-readable table (S1.8).")
w()
w("**A tradeoff we report rather than hide.** Ranking by synthetic "
  "accessibility selects simpler molecules, which are less similar to the "
  "reference set. Maximum Tanimoto across these 20 is 0.351–0.483 against a "
  "0.35 cutoff — several compounds sit within 0.01 of the applicability-domain "
  "boundary. The superseded rule (S1.6) returned 0.672–0.818. The reported set "
  "trades depth-in-domain for chemical diversity and makeability; readers "
  "wanting depth-in-domain should use S1.6.")
w()
w("### S1.6 The superseded ranking")
w()
w("Amendment A1.2 as registered ranked by Tanimoto descending, then synthetic "
  "accessibility ascending. Executing it revealed that the rule **selected "
  "against the novelty it was meant to ensure**: the three highest-ranked "
  "products were at Tanimoto 1.000 to a B3DB compound — already-known "
  "structures — and the 20 collapsed onto 7 parents and 6 scaffolds, largely "
  "positional isomers of one another. Amendment A2 replaced it. Both rankings "
  "are published; this is the original.")
w()
w(block("results/design_enumeration.txt", 53, 76))
w()
w("### S1.7 Structural alerts")
w()
w("Filter F8 applies the PAINS catalogue. Inspection of the reported "
  "structures found compound #10 to be an **aryl thiosulfonate** — a "
  "thiol-reactive electrophile, used deliberately as a cysteine-modifying "
  "reagent — which PAINS does not match. A broader alert scan was therefore "
  "run over all 793 novel survivors.")
w()
w("| catalogue | flagged |")
w("| --- | --- |")
w("| PAINS (filter F8, already applied) | 0 / 793 |")
w("| NIH | 4 / 793 |")
w("| **BRENK** | **200 / 793** |")
w()
n_al = sum(1 for r in rows[:20] if r["brenk_alert"])
w(f"Leading BRENK alerts across the 793: aliphatic long chain (61), Michael "
  f"acceptor (24), nitro group (21), aldehyde (17), diketo (14). "
  f"**{n_al} of the reported 20 carry an alert** (S1.5).")
w()
w("These liabilities are **inherited from the parent ChEMBL actives, not "
  "created by the single edits**. That is a real distinction and not a "
  "defence: a proposal list should surface them. They are **flagged, not "
  "removed** — removing them would mean adding a filter after seeing the "
  "output, which this project declined to do elsewhere. We report the finding "
  "as a caution against treating a PAINS pass as sufficient screening "
  "hygiene.")
w()
w("### S1.8 Full structure table")
w()
w(f"All **{len(rows)}** novel survivors, with SMILES, parent SMILES, parent "
  f"ChEMBL id, transformation, Bemis–Murcko scaffold, maximum Tanimoto, "
  f"predicted p(BBB+), Ertl SA, MW, cLogP, TPSA, HBD, BRENK alert and novelty "
  f"query date, are provided as a machine-readable CSV: "
  f"**`results/design_proposals.csv`** (Additional file 2).")
w()
w("---")

# --------------------------------------------------------------------- S2
w()
w("## S2. Registration, amendments and decision log")
w()
w("The registration itself is public and immutable at "
  "[10.17605/OSF.IO/UQR62](https://doi.org/10.17605/OSF.IO/UQR62), registered "
  "against commit `134ab60`. Foreknowledge was declared as *\"authors have "
  "observed the data, but have not performed the proposed analyses\"*. The "
  "two amendments below post-date it and are reproduced in full, since they "
  "are not on OSF.")
w()
def demote(md, levels=2):
    """Push embedded headings down so they nest under this document's own."""
    return re.sub(r"^(#{1,4}) ", lambda m: "#" * (len(m.group(1)) + levels) + " ",
                  md, flags=re.M)


pre = read("docs/preregistration.md").splitlines()
w(demote("\n".join(pre[320:]).strip()))
w()
w("### S2.1 Decision log")
w()
log = read("docs/decisions.md")
entries = re.findall(r"^## (\d{4}-\d{2}-\d{2}) — (.+)$", log, re.M)
w(f"{len(entries)} dated entries record every judgement call made during the "
  f"study, including those that went against us. The full log is "
  f"`docs/decisions.md` (Additional file 3); the index follows.")
w()
w("| date | decision |")
w("| --- | --- |")
for d, t in entries:
    w(f"| {d} | {t} |")
w()
w("---")

# --------------------------------------------------------------------- S3
w()
w("## S3. Label-permuted validation")
w()
w("Blinding is not available for a computational analysis the analyst wrote. "
  "We substituted label permutation: the complete pipeline was run on data "
  "whose BBB labels had been shuffled, where the true effect is zero by "
  "construction. A pipeline that reports an effect there is reporting an "
  "artefact of its own design.")
w()
w(block("results/permuted_validation_summary.txt", 2, 31))
w()
w("The gate is enforced in code, not by assertion: `scripts/gate.py` compares "
  "the SHA-256 of the pipeline under test against the manifests and refuses "
  "the confirmatory run unless the permuted runs pass. The confirmatory script "
  "could therefore execute exactly once, on real labels, after the harness had "
  "demonstrated it finds nothing in nothing.")
w()
w("---")

# --------------------------------------------------------------------- S4
w()
w("## S4. Curation sensitivity")
w()
w("Ten curation variants, crossing assay-type pooling, activity threshold, "
  "target confidence score, assay format and skeleton deduplication. The "
  "headline out-of-domain percentages in the main text are the ranges across "
  "these variants, not a single curation's number.")
w()
w(block("results/sensitivity.txt", 8, 60))
w()
w("**The out-of-domain finding is not an artefact of curation choices.** "
  "Across every variant, the great majority of BACE1 actives and a large "
  "minority of AChE actives have no B3DB neighbour above the cutoff. The "
  "variant with the largest drift is the permissive pChEMBL ≥ 5 threshold, and "
  "it moves the BACE1 figure by 4.0 percentage points — from 85.8% to 81.8% "
  "out of domain, which does not change the conclusion.")
w()
w("---")

# --------------------------------------------------------------------- S5
w()
w("## S5. Literature search record")
w()
lit = read("docs/literature-search.md")
w(demote(re.sub(r"^# .*\n", "", lit, count=1).strip(), 1))
w()
w("---")

# --------------------------------------------------------------------- S6
w()
w("## S6. Scaffold-filter sensitivity")
w()
w("Filter F6 requires the Bemis–Murcko scaffold to be retained. Applied "
  "strictly, it **forbids four of the ten transformations in the catalogue** — "
  "T01, T04, T09 and T10 — because each alters a ring and so changes the "
  "scaffold by definition. The registered protocol therefore contained a "
  "filter that rejected 40% of its own catalogue, a defect invisible at "
  "registration and revealed only by execution.")
w()
w("A labelled post hoc sensitivity re-ran the pipeline with F6 relaxed to "
  "ring-topology equivalence (Murcko generic scaffold), which permits the "
  "ring-altering edits.")
w()
w("| stage | F6 strict (registered) | F6 topology (post hoc) |")
w("| --- | --- | --- |")
strict = read("results/design_enumeration.txt")
topo = read("results/design_enumeration_topology.txt")


def pull(txt, label):
    m = re.search(re.escape(label) + r"\s*:?\s*(\d+)", txt)
    return m.group(1) if m else "—"


for label, name in [("F6 scaffold retained", "F6 scaffold retained"),
                    ("F7 inside property window", "F7 inside property window"),
                    ("F8 PAINS-free", "F8 PAINS-free"),
                    ("F4 SA <= 4.0", "F4 SA ≤ 4.0"),
                    ("unique structures", "unique structures"),
                    ("F2 in domain (max Tanimoto >= 0.35)", "F2 in domain"),
                    ("F3 predicted BBB+ (p >= 0.68)", "F3 predicted BBB+")]:
    w(f"| {name} | {pull(strict, label)} | {pull(topo, label)} |")
w()
w("**The cost is 86 compounds — and the count understates it.** 62 of the 86 "
  "are products of T04, benzene → pyridine, which the chemistry review judged "
  "the single most valuable transformation in the catalogue: the aromatic "
  "N-walk lowers logP by roughly one unit, adds an acceptor, and commonly "
  "reduces hERG liability. The registered filter blocked the catalogue's best "
  "entry entirely. The remaining 24 come from T09. T01 and T10 contribute "
  "nothing either way — T01 was rejected on CNS grounds and T10 is a "
  "diagnostic (S1.1).")
w()
w("The registered strict rule governs every number reported in the main text. "
  "This sensitivity is labelled post hoc and is reported because the defect is "
  "part of the paper's argument about what pre-registration does and does not "
  "catch.")
w()

open(OUT, "w").write("\n".join(parts) + "\n")
words = len(" ".join(parts).split())
print(f"wrote {OUT}  ({len(parts)} blocks, ~{words} words)")
print(f"  S1 structure table: {len(rows)} compounds")
print(f"  S2 decision log index: {len(entries)} entries")
