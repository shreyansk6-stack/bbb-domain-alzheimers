# Chemistry review — questions for the co-author

**For: Samuel Siyanbola. ~15 minutes.** Write answers inline under each question.
Short answers are fine; "no opinion" is a legitimate answer and better than a guess.

Open `results/design_proposals.png` alongside this (6 parent/product pairs, changed
atom highlighted) and `results/design_proposals.txt` (the top 20 table and SMILES).

Background: we enumerate single medicinal-chemistry edits on 2,391 curated AChE
actives, keep only products that stay inside the BBB model's applicability domain,
and propose them as compounds *on which a BBB prediction can be defended*. We make
**no claim of activity** and apply no activity model. Nothing is being synthesised.

---

## Q1. The catalogue — is each of these a move you'd actually make?

This is the main question. For each, answer **keep / drop / keep with changes**.

| id | transformation | products surviving all filters |
| --- | --- | --- |
| T01 | carboxylic acid → tetrazole | 0 (blocked, see Q2) |
| T02 | carboxylic acid → primary amide | 0 |
| T03 | methyl ester → primary amide | 0 |
| T04 | benzene → pyridine (aromatic N-walk) | 0 (blocked, see Q2) |
| T05 | aromatic fluorine scan | **471** |
| T06 | aromatic chlorination | **267** |
| T07 | methyl → ethyl homologation | 11 |
| T08 | tertiary amine N-demethylation | 44 |
| T09 | morpholine → piperidine | 0 (blocked, see Q2) |
| T10 | piperidine → morpholine | 0 (blocked, see Q2) |

**T01** →
**T02** →
**T03** →
**T04** →
**T05** →
**T06** →
**T07** →
**T08** →
**T09** →
**T10** →

**Q1b. Anything obviously missing** that belongs in a catalogue of single edits for
improving CNS exposure of an AChE inhibitor series?

→

---

## Q2. Four transformations are blocked by our own filter. Does that cost us anything?

T01, T04, T09 and T10 each change a **ring atom**, so the Bemis–Murcko scaffold
changes, so our scaffold-retention filter rejects 100% of their products (1,551
compounds) before any chemistry is considered. We are reporting this as a design
defect and are **not** relaxing the filter.

We need to know how much good chemistry it cost. Specifically:

**Q2a. Is benzene → pyridine (T04) a move you'd want in the list?** It is the one we
suspect matters most — lowers logP, adds an acceptor, standard CNS move. 62 products
would survive if the filter were relaxed.

→

**Q2b. Are the ring replacements (T09/T10, morpholine ↔ piperidine) worth having?**

→

**Q2c. Is acid → tetrazole (T01) worth having**, given only 23 of 2,391 AChE actives
contain a carboxylic acid at all?

→

---

## Q3. The output is 93% halogen scans. Is that worth proposing?

Of 793 novel survivors: 471 fluorine scan, 267 chlorination, 44 N-demethylation, 11
methyl→ethyl.

**Q3a. Is "add a fluorine or chlorine to a known AChE inhibitor" a proposal a
medicinal chemist would take seriously**, or is it decoration we should describe more
modestly?

→

**Q3b. Aromatic chlorination (T06) specifically.** It was included partly so the
property filter had something to reject. For a CNS target, is adding an aromatic Cl
usually a reasonable move, or usually the wrong direction?

→

---

## Q4. Curation criteria — the sign-off you were always meant to give

These set which ChEMBL compounds count as AChE actives. They are already fixed in
the registration; we need your agreement on record, or your objection documented.

**Q4a. pChEMBL ≥ 6 (1 µM) as the activity threshold.** Right for AChE?

→

**Q4b. IC50 and Ki pooled, Kd excluded, replicates aggregated by median.** Acceptable?
(Note: potency never enters any model — it only decides set membership.)

→

**Q4c. Assay confidence score 9 only.** This keeps human AChE and excludes
*Electrophorus* and *Torpedo* enzyme assays, which are common in the literature. We
judged their inhibitor SAR too different to pool. Agree?

→

---

## Q5. The property window killed the acid isosteres

Filter: **MW ≤ 450, cLogP 1–4, TPSA ≤ 90.**

**Q5a. Is that the right CNS window**, or would you use something else (CNS MPO, a
different logP range, an HBD limit)?

→

**Q5b. The lower cLogP bound of 1** is what removes the amide products (T02/T03).
Keep it, or is it doing harm?

→

---

## Q6. Look at the top 20 — does anything look wrong?

Open `results/design_proposals.png` and the SMILES list in
`results/design_proposals.txt`.

**Q6a. Does any structure look unmakeable, unstable, or obviously silly?** Numbers
are enough.

→

**Q6b. The reported 20 sit at Tanimoto 0.35–0.48 to the reference set** — just inside
our domain cutoff of 0.35. The alternative ranking gives compounds at 0.67–0.82 but
only 6 distinct scaffolds instead of 20. **Which table would you put in the paper?**

→

---

## Q7. Two editorial calls

**Q7a. Does the design component belong in the main text, or in supplementary?** It is
exploratory and claims no activity; the rest of the paper is a methods audit.

→

**Q7b. Author contributions.** Current draft: "S.S. contributed medicinal-chemistry
judgement on curation criteria and the transformation catalogue, and critical
revision." Accurate once this review is done?

→

---

_Answers get recorded in `docs/decisions.md` with the date, and the catalogue's
`status` fields in `config/transformations.json` updated from `proposed` to
`approved` or `rejected` with the reasoning._
