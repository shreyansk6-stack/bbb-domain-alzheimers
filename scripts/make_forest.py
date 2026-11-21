"""Forest plot of every dAUC estimate in the study, for the manuscript.

One figure carrying the primary endpoint, both control arms, the cutoff
sensitivity, the alternative domain definitions and the secondary model, with
the pre-registered support threshold and refutation band marked. Reading it
should make the paper's central claim - a small effect that no comparison
resolves - visible at a glance.

Usage: ./env/bin/python -I scripts/make_forest.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

real = json.load(open("results/confirmatory_real.json"))
cuts = json.load(open("results/secondary_cutoffs.json"))["cutoffs"]
defs = json.load(open("results/secondary_domain_defs.json"))["definitions"]
desc = json.load(open("results/secondary_descriptor_model.json"))

rows = []


def add(label, d, lo, hi, group, primary=False):
    rows.append(dict(label=label, d=d, lo=lo, hi=hi, group=group, primary=primary))


p = real["results"]["property"]
r = real["results"]["random"]
add("property-matched control", p["delta"], p["lo"], p["hi"], "PRIMARY", True)
add("unmatched random control", r["delta"], r["lo"], r["hi"], "PRIMARY")
for c in ("0.3", "0.35", "0.4"):
    k = c if c in cuts else {"0.3": "0.3", "0.4": "0.4"}.get(c)
    if k in cuts:
        v = cuts[k]
        add(f"Tanimoto {float(k):.2f}  (n={v['n']})", v["delta"], v["lo"], v["hi"], "CUTOFF")
for name, v in defs.items():
    add(f"{name}  (n={v['n']})", v["delta"], v["lo"], v["hi"], "DOMAIN DEFINITION")
dp = desc["results"]["property"]
add("descriptor gradient boosting", dp["delta"], dp["lo"], dp["hi"], "MODEL")

rows = rows[::-1]
fig, ax = plt.subplots(figsize=(9.5, 0.46 * len(rows) + 2.0))

ax.axvspan(-0.03, 0.03, color="#d8d8d8", alpha=0.55, zorder=0)
ax.axvline(0, color="#444", lw=1.0, zorder=1)
ax.axvline(0.06, color="#b03030", lw=1.1, ls="--", zorder=1)

# rows are drawn bottom-up, so a group's label belongs at its highest index
tops = {}
for i, row in enumerate(rows):
    tops[row["group"]] = max(tops.get(row["group"], i), i)

for i, row in enumerate(rows):
    colour = "#1a1a1a" if row["primary"] else "#4a6fa5"
    ax.plot([row["lo"], row["hi"]], [i, i], color=colour,
            lw=2.6 if row["primary"] else 1.7, solid_capstyle="round", zorder=3)
    ax.plot([row["d"]], [i], "o", color=colour,
            ms=8 if row["primary"] else 6, zorder=4)
    if tops[row["group"]] == i:
        ax.text(-0.075, i + 0.40, row["group"], fontsize=7.5, color="#888",
                fontweight="bold", va="bottom")

ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r["label"] for r in rows], fontsize=9)
ax.set_ylim(-0.8, len(rows) - 0.1)
ax.set_xlabel("ΔROC-AUC   (control − proximal; positive = worse on target-proximal chemistry)",
              fontsize=9.5)
ax.set_xlim(-0.075, 0.145)
ax.tick_params(axis="x", labelsize=9)
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)
ax.text(0.062, len(rows) - 0.55, "pre-registered\nsupport threshold", fontsize=7.5,
        color="#b03030", va="top")
ax.text(0.0, -0.72, "refutation band (±0.03)", fontsize=7.5, color="#777",
        ha="center", va="bottom")
ax.set_title("No comparison in this study resolves the effect", fontsize=11.5,
             fontweight="bold", loc="left", pad=14)
fig.tight_layout()
fig.savefig("results/fig2_forest.png", dpi=200)
print("wrote results/fig2_forest.png")
