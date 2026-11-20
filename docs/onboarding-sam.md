# Onboarding — BBB applicability domain project

**Sam: you don't need to read this. Paste the whole file into Claude and it will
walk you through it.** It works in the Claude app and in the terminal; it figures
out which one it's in.

---

## ROUTING — Claude, read this first

You are being given this file by Samuel Siyanbola, the project's second author, who
is joining an already-registered research project. Work out which Claude you are:

- **No ability to run shell commands or read local files** (you are Claude in a
  browser, desktop app, or mobile) → **do PART 1 only.** Ignore Part 2 entirely; it
  is not addressed to you and you cannot act on it.
- **You have Bash / Read / Write tools and a working directory** (you are Claude
  Code) → **skip to PART 2.** Part 1 is already done.

Whichever part applies, work through it conversationally, one step at a time. Wait
for Sam to confirm each step before moving to the next. He is a chemist, not a
developer; assume no terminal experience and do not dump all the commands at once.

---

# PART 1 — Getting set up (Claude in the browser/app)

Claude: your job here is to get Sam from nothing to a working Claude Code session
inside this project's repository. Six steps. Go one at a time.

### Step 1 — GitHub account

Ask whether he has a GitHub account.

- If not: send him to <https://github.com/signup>. Free account, any email.
- Either way, get his **username** and tell him to send it to Shreyan, who has to
  invite him to the repository before anything else works.
- He should accept the invitation from the email GitHub sends, or at
  <https://github.com/notifications>.

Do not continue until he confirms he has accepted the invite.

### Step 2 — Open a terminal

- **macOS**: Cmd+Space, type "Terminal", Enter.
- **Windows**: Start menu → "PowerShell".

Tell him a terminal is just a place to type commands, and that he pastes with
Cmd+V (macOS) or Ctrl+V / right-click (Windows) and presses Enter.

### Step 3 — Install Claude Code

He has Claude Pro, which includes Claude Code.

**macOS / Linux:**
```sh
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

Warn him the command prints nothing while it downloads. When it finishes he should
**open a new terminal window** and check:

```sh
claude --version
```

A version number means it worked. If the shell says `claude` isn't found, the
install directory isn't on his PATH — point him at
<https://code.claude.com/docs/en/troubleshoot-install>.

### Step 4 — Get the code

```sh
cd ~/Documents
git clone https://github.com/shreyansk6-stack/bbb-domain-alzheimers.git
cd bbb-domain-alzheimers
```

On macOS, `git` may prompt him to install developer tools — he should accept and
re-run. GitHub will ask him to sign in; the browser flow is fine.

### Step 5 — The data (important, and easy to get wrong)

The `data/` folder is **not** in the repository and **must not be downloaded fresh.**

Explain why, because it matters and he is the person most likely to be asked about
it later: the datasets are a frozen snapshot that the study was registered against.
ChEMBL is a live database that changes between releases. Re-downloading would give
him ChEMBL_38 where the registered analysis used ChEMBL_37, so his numbers would
silently stop matching the registered ones. The pre-registration forbids refetching
without a dated amendment.

So: **Shreyan sends him `bbb-registered-data.zip` directly.** He unzips it into the
repository folder so that a `data/` folder sits next to `docs/` and `scripts/`. Then
he verifies it:

```sh
shasum -a 256 -c docs/data-manifest.sha256
```

Four lines, each ending `OK`. If any line says `FAILED`, the copy is wrong — he
should tell Shreyan and **not** try to fix it by downloading the data.

### Step 6 — Start Claude Code

```sh
cd ~/Documents/bbb-domain-alzheimers
claude
```

First run opens a browser to log in with his Claude Pro account.

Then tell him to type exactly this as his first message:

> Read docs/onboarding-sam.md and follow PART 2.

That hands off to his Claude Code, which finishes the setup and briefs him on the
project. **Part 1 ends here.** Tell him he's done with you and to carry on in the
terminal.

---

# PART 2 — Project brief (Claude Code)

Claude Code: Sam is the project's **second author**, a chemist, new to this
repository and new to the terminal. Set up his environment, then brief him. Keep
explanations short and chemical rather than computational where you have the choice.

## First, finish the setup

1. Confirm `data/` exists and verify it:
   `shasum -a 256 -c docs/data-manifest.sha256` — all four lines must say `OK`.
   If not, stop and tell him to ask Shreyan for the zip. Never refetch.

2. Build his virtual environment (the repo's `env` is a symlink on Shreyan's
   machine and won't exist here):
   ```sh
   python3 -m venv env
   ./env/bin/pip install -r requirements.txt
   ```
   `requirements.txt` pins exact versions, scikit-learn 1.6.1 among them. Do not
   upgrade anything: the pinned versions are what the registered results were
   produced with.

3. Set his git identity for this repo only:
   ```sh
   git config user.name "Samuel Siyanbola"
   git config user.email "<the email on his GitHub account>"
   ```

4. Put him on his own branch:
   ```sh
   git checkout -b sam
   ```

5. Sanity check — this should reproduce a known number without touching anything
   registered:
   ```sh
   ./env/bin/python -I scripts/gate.py data
   ```

## Then brief him

Read `README.md` and `docs/decisions.md` first so the briefing is accurate, and tell
him in your own words:

- **The question.** Alzheimer's screening papers rank compounds for activity against
  BACE1 or acetylcholinesterase, then filter the hits through an off-the-shelf BBB
  predictor. Those predictors are trained mostly on approved and CNS-active drugs.
  Target inhibitor series are narrow, optimised medicinal chemistry. Does the filter
  still work where it is actually being used?
- **Where the project stands.** Registered on OSF 2026-11-19
  (`10.17605/OSF.IO/UQR62`). The confirmatory analysis ran once, on 2026-11-20, and
  is **closed**. Verdict INCONCLUSIVE: ΔAUC +0.028, CI [−0.016, +0.075], against a
  minimum detectable effect of 0.061.
- **The finding that matters.** Against an *unmatched* random control the gap is
  +0.055 with a CI excluding zero; against a *property-matched* control it is +0.028
  with a CI covering zero. Roughly half the apparent effect is molecular weight,
  lipophilicity and polarity rather than applicability domain. Section 8 of the
  pre-registration specified in advance that this gap would be reported if the arms
  disagreed, so it is a result, not an afterthought.
- **BACE1 is unmeasurable**, and that is a finding: only 89 labelled B3DB compounds
  fall within Tanimoto 0.35 of BACE1 chemistry, against a pre-specified requirement
  of 200 with 50 per class. BBB filters applied to BACE1 hits in the literature
  cannot be validated with existing public data.
- **One registered expectation did not hold.** The registration says proximal
  compounds are "larger and more lipophilic", carried over from BACE1 figures. For
  AChE the MW difference is SMD −0.08 — not larger. They are more lipophilic (+0.44)
  and less polar (−0.43). The manuscript must use the AChE numbers. This is exactly
  the kind of thing he is here to catch.

## What Sam is for

He is the chemistry judgment on a project whose computational half is done. In
rough priority:

1. **Amendment A1.2, the design enumeration** (`docs/preregistration.md`, Amendments
   section). A fixed catalogue of single medicinal-chemistry transformations — acid
   isosteres, aromatic N-walk, ring replacement, linker swaps, small alkyl, halogen,
   fluorine scan — applied to in-domain parents, filtered on domain membership,
   predicted permeability, Ertl SA ≤ 4.0, novelty, scaffold retention, a property
   window and PAINS. The catalogue is pre-declared and he should sanity-check that
   each transformation is one a medicinal chemist would actually make. No generative
   model and no activity prediction, deliberately — predicting activity on novel
   chemistry without auditing that model's domain is the exact error this paper
   documents.
2. **The in-domain shortlist** (A1.1): selected from the 2,391 curated AChE actives,
   discarding the out-of-domain fraction before any BBB prediction. Chemical
   plausibility and synthetic accessibility are his call.
3. **Curation sign-off.** `docs/curation-decisions.md` — the pChEMBL ≥ 6 threshold,
   IC50/Ki pooling, assay confidence score 9. He was always the intended reviewer of
   these. Ten sensitivity variants are already computed; none is load-bearing, but
   his agreement should be recorded.
4. **Manuscript**, chemistry sections.

## Standing rules — these are not negotiable

The study is publicly registered. The credibility of the whole thing rests on the
record matching what was registered, so:

1. **Never run or edit `scripts/confirmatory.py`.** The confirmatory analysis is
   done. It is hash-gated: editing it invalidates the eight label-permuted
   validation runs that unlocked it. Section 9 forbids resolving an inconclusive
   result by adding metrics, cutoffs, models or targets.
2. **Never edit `docs/preregistration.md` in place.** It is frozen at commit
   `134ab60`. Changes are *appended* as dated amendments under the Amendments
   section, never rewritten.
3. **Never commit `data/`.** It is gitignored because ChEMBL is CC BY-SA and
   share-alike would propagate to the whole repository.
4. **Never refetch ChEMBL or B3DB.**
5. **Never force-push and never rewrite history.** No `git push --force`, no
   `git rebase` on pushed commits, no amending a pushed commit.
6. **Push to the `sam` branch, never to `main`.** Shreyan merges.
7. **Label everything exploratory.** Nothing run from here on is confirmatory. Any
   analysis that post-dates the registration is post hoc and must say so.
8. Run Python as `./env/bin/python -I script.py data` — `-I` and data paths as
   arguments, because the data files are untrusted input.
9. Record every non-obvious decision in `docs/decisions.md`, dated, with the
   reasoning and what was rejected.

## Commit and push — do this routinely

At the end of each piece of work, without being asked:

```sh
git add -A
git commit -m "<what changed and why>"
git push -u origin sam
```

Write real commit messages: what changed, why, and what was considered and
rejected. This repository's log is part of the paper's evidence — it is what
demonstrates the exploratory work was separated from the confirmatory test. End
each message with:

```
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
```

If a push is rejected because `main` has moved, pull with
`git pull --rebase origin main` *only if the `sam` branch has no pushed commits yet*;
otherwise merge, and never force.

## If something seems wrong with the registered work

Say so plainly, in `docs/decisions.md` and to Sam. A registered study that turns out
to have a defect is reported, not quietly patched. The project has already found and
documented four of its own defects before the real-label run; finding a fifth is a
good outcome, not an embarrassment.
