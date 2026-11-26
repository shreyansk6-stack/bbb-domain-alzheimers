# bbb-domain-alzheimers

Pre-registered methods audit: applicability domain of BBB predictors in Alzheimer's
target chemical space. **Single-author paper** (S.K.); the prospective second
author withdrew on 2026-11-25 having made no contribution. Manuscript is
**submitted to *Journal of Cheminformatics* on 2026-11-25** and in Technical
Check. `docs/submission-record.md` holds what was uploaded and the one open
item: the APC waiver application, due 2026-12-09. `docs/decisions.md` is frozen
at 27 entries until revision, because the manuscript, the SI and the gate all
state that count;
`docs/submission-checklist.md` holds the order of operations.

Start by reading `docs/submission-checklist.md` — it holds current state, what is
ready, what is waiting, and the order of operations at submission. Do not duplicate
that content here.

## Hard constraints — do not violate

- **Never edit or re-run `scripts/confirmatory.py`.** It is SHA-256 hash-gated via
  `scripts/gate.py`; the confirmatory analysis is closed. Numbers come from
  `results/confirmatory_real.{json,txt}`. Anything needing those internals parses the
  recorded text.
- **`docs/preregistration.md` is frozen.** Amendments are appended and labelled post
  hoc; the registered text is never altered. One exception, made deliberately on
  2026-11-25 at the author's instruction: the authorship lines and section 13 were
  edited to match the OSF contributor removal, each labelled "Amended 2026-11-25".
- **`data/` stays gitignored.** ChEMBL is CC BY-SA; redistribution would trigger
  share-alike.
- **Run anything touching downloaded data with `python3 -I`** and pass data paths as
  arguments.
- **Use a generic User-Agent for external API calls.** Never send the user's personal
  email to an external service.

## Before any commit or submission

```
./env/bin/python -I scripts/check_consistency.py     # 79 assertions, must be 79/79
```

It checks every headline number in the manuscript, SI and cover letter against the
result file that produced it, and fails on leftover placeholders. It exists because a
prose-only number drifted once (§4.3 read 1,551 where the funnels give 1,516). **Any
new number that appears only in prose gets an assertion added here.** It also
asserts that every listed reference is cited in the text.

## Regenerating artifacts

```
./env/bin/python -I scripts/make_figures.py          # Figures 1, 3
./env/bin/python -I scripts/make_forest.py           # Figure 2
./env/bin/python -I scripts/make_fig4.py             # Figure 4, from recorded JSON
./env/bin/python -I scripts/build_supplementary.py   # docs/supplementary.md (S1-S6)
./env/bin/python -I scripts/render_manuscript.py     # docs/manuscript.html
./env/bin/python -I scripts/finalize_submission.py   # submission copy, at submission only
```

`docs/manuscript.md` is the working draft and carries a DRAFT banner. Never upload it.
`finalize_submission.py` generates the clean copy and refuses to write one if the
consistency check fails or a placeholder survives.

## Conventions

- Decisions get a dated entry appended to `docs/decisions.md`. 27 entries so far; it
  ships as an additional file.
- Git identity is local to this repo: Shreyan Kancharla <shkancharla@davidson.edu>.
- Two working copies exist: `~/Desktop/bbb-domain-alzheimers` (current) and
  `~/Documents/bbb-domain-alzheimers` (was macOS-TCC-blocked). Everything is pushed;
  `git pull` the Documents copy before using it, then delete whichever is unwanted.
