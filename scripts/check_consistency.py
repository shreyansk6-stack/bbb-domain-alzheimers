"""Pre-submission check: do the documents agree with the recorded results?

Every claim below is a number that appears in the manuscript, the supplementary
information or the cover letter, checked against the file that produced it. A
mismatch means a document drifted from its analysis, which is the failure mode
this project has been guarding against throughout.

Exit status is non-zero if anything fails, so this can gate a submission.

Usage: ./env/bin/python -I scripts/check_consistency.py
"""
import csv
import json
import re
import sys

DOCS = {
    "manuscript": "docs/manuscript.md",
    "supplementary": "docs/supplementary.md",
    "cover letter": "docs/cover-letter.md",
}
text = {k: open(v).read() for k, v in DOCS.items()}

real = json.load(open("results/confirmatory_real.json"))
nov = json.load(open("results/novelty.json"))
defs = json.load(open("results/secondary_domain_defs.json"))["definitions"]
enum_txt = open("results/design_enumeration.txt").read()
topo_txt = open("results/design_enumeration_topology.txt").read()
with open("results/design_proposals.csv") as fh:
    rows = list(csv.DictReader(fh))

checks, failures = [], []


def want(label, value, docs, pattern=None):
    """Assert `value` appears in each named document.

    Prose writes four-figure numbers with a thousands separator while the
    verbatim result blocks do not, so a bare integer matches either form.
    """
    if pattern:
        pat = pattern
    elif isinstance(value, int) and value >= 1000:
        d = str(value)
        pat = re.escape(d[:-3]) + ",?" + re.escape(d[-3:])
    else:
        pat = re.escape(str(value))
    for d in docs:
        ok = re.search(pat, text[d]) is not None
        checks.append((ok, f"{label} = {value}", d))
        if not ok:
            failures.append(f"{label} ({value}) not found in {d}")


def same(label, a, b):
    ok = a == b
    checks.append((ok, f"{label}: {a} == {b}", "results"))
    if not ok:
        failures.append(f"{label}: {a} != {b}")


# ---------------------------------------------------- internal consistency
f3 = int(re.search(r"F3 predicted BBB\+.*?:\s*(\d+)", enum_txt).group(1))
f3_topo = int(re.search(r"F3 predicted BBB\+.*?:\s*(\d+)", topo_txt).group(1))
same("novel + known == F3 survivors", nov["n_novel"] + nov["n_known"], f3)
same("CSV rows == novel count", len(rows), nov["n_novel"])
same("topology gain == 86", f3_topo - f3, 86)
same("primary n == proximal n", real["proximal"]["n"], 492)

prop = real["results"]["property"]
same("delta rounds to 0.028", round(prop["delta"], 3), 0.028)
same("CI is the recorded one",
     (round(prop["lo"], 4), round(prop["hi"], 4)), (-0.0164, 0.0749))

brenk20 = sum(1 for r in rows[:20] if r["brenk_alert"])
same("BRENK in top 20 == 7", brenk20, 7)
same("scaffolds in top 20 == 20",
     len({r["scaffold"] for r in rows[:20]}), 20)
same("parents in top 20 == 20",
     len({r["parent_chembl"] for r in rows[:20]}), 20)

tan = [float(r["max_tanimoto"]) for r in rows[:20]]
same("top-20 Tanimoto range", (min(tan), max(tan)), (0.351, 0.483))

# ------------------------------------------------- documents vs the results
want("curated AChE actives", 2391, ["manuscript", "supplementary"])
want("B3DB reference", 3892, ["manuscript", "supplementary"])
want("proximal holdout n", 492, ["manuscript", "supplementary"])
want("F3 survivors", f3, ["manuscript", "supplementary"])
want("novel survivors", nov["n_novel"], ["manuscript", "supplementary"])
want("primary delta", "0.028", ["manuscript", "cover letter"])
want("F6 cost", 86, ["manuscript", "supplementary"])

# numbers that live only in prose and so can drift unnoticed
f6_blocked = int(re.search(r"F6 scaffold retained\s*:\s*(\d+)",
                           topo_txt).group(1)) - \
    int(re.search(r"F6 scaffold retained\s*:\s*(\d+)", enum_txt).group(1))
same("F6 blocks 1516 ring-altering products", f6_blocked, 1516)
want("F6 blocked products", f6_blocked, ["manuscript"])

power = open("results/power.txt").read()
bace_n, bace_mde = re.search(
    r"BACE1 at 0\.35 \(n=\s*(\d+)\): SE [\d.]+\s+MDE dAUC ~ ([\d.]+)",
    power).groups()
want("BACE1 n", int(bace_n), ["manuscript"])
want("BACE1 MDE", bace_mde, ["manuscript"])
want("parents", len({r["parent_chembl"] for r in rows}), ["manuscript",
                                                          "supplementary"])
want("scaffolds", len({r["scaffold"] for r in rows}), ["manuscript"])
want("BRENK flagged", 200, ["manuscript", "supplementary"])
want("registration DOI", "10.17605/OSF.IO/UQR62",
     ["manuscript", "supplementary", "cover letter"])
want("ORCID (S.K.)", "0009-0009-8654-110X", ["cover letter", "manuscript"])
want("ORCID (S.S.)", "0009-0002-0657-1528", ["manuscript"])
want("Jaccard C/D identical", "1.000", ["supplementary", "manuscript"],
     pattern=r"1\.000")
want("scaffold Jaccard", "0.010", ["manuscript"], pattern=r"0\.010")

# ------------------------------------------------------- hygiene / leftovers
for name, body in text.items():
    for pat, why in [(r"\[AUTHORS(?!: suggested reviewers)",
                      "unresolved [AUTHORS] marker"),
                     (r"\bTODO\b", "TODO left in text"),
                     (r"XXX|FIXME", "placeholder left in text"),
                     (r"\[to be completed\]", "incomplete placeholder")]:
        hit = re.search(pat, body)
        ok = hit is None
        checks.append((ok, why, name))
        if not ok:
            failures.append(f"{why} in {name}")

# the draft banner must be removed before submitting, but should exist now
banner = "DRAFT" in text["manuscript"][:1200]
checks.append((banner, "draft banner present (remove at submission)",
               "manuscript"))

pending = re.search(r"\[AUTHORS: suggested reviewers", text["cover letter"])
print()
print("PENDING (expected, not failures):")
print("  - suggested reviewers not yet chosen" if pending else
      "  - none; reviewers chosen")
print("  - S.S. has not yet read and approved the manuscript")

# ------------------------------------------------------------------ report
width = max(len(c[1]) for c in checks) + 2
print("=" * (width + 18))
print("PRE-SUBMISSION CONSISTENCY CHECK")
print("=" * (width + 18))
for ok, label, where in checks:
    print(f"  {'PASS' if ok else 'FAIL'}  {label:<{width}} {where}")
print()
print(f"{sum(1 for c in checks if c[0])}/{len(checks)} passed")
if failures:
    print("\nFAILURES:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("\nAll checks passed.")
