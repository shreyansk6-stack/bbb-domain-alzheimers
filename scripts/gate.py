import json, sys
import pandas as pd, numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator, Descriptors, inchi
from rdkit.Chem.Scaffolds import MurckoScaffold
from rdkit import DataStructs
RDLogger.DisableLog('rdApp.*')

DATA = sys.argv[1]
gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)

def prep(smiles_list, ids):
    fps, keys, scaffs, props, kept = [], [], [], [], []
    for smi, i in zip(smiles_list, ids):
        m = Chem.MolFromSmiles(smi) if isinstance(smi, str) else None
        if m is None: continue
        fps.append(gen.GetFingerprint(m))
        try: keys.append(inchi.MolToInchiKey(m))
        except Exception: keys.append(None)
        try: scaffs.append(MurckoScaffold.MurckoScaffoldSmiles(mol=m))
        except Exception: scaffs.append(None)
        props.append((Descriptors.MolWt(m), Descriptors.MolLogP(m), Descriptors.TPSA(m)))
        kept.append(i)
    return fps, keys, scaffs, np.array(props), kept

# --- B3DB ---
b3 = pd.read_csv(f"{DATA}/B3DB_classification.tsv", sep="\t")
b3 = b3.dropna(subset=["SMILES"])
b_fps, b_keys, b_scaffs, b_props, b_idx = prep(b3["SMILES"].tolist(), b3.index.tolist())
b3 = b3.loc[b_idx].reset_index(drop=True)
labels = b3["BBB+/BBB-"].astype(str).values
print(f"B3DB parsed: {len(b_fps)}  (BBB+: {(labels=='BBB+').sum()}, BBB-: {(labels=='BBB-').sum()})")

# --- targets ---
acts = json.load(open(f"{DATA}/chembl_actives.json"))
T = {}
for name, d in acts.items():
    ids = list(d.keys()); smis = [d[i] for i in ids]
    f, k, s, p, kept = prep(smis, ids)
    T[name] = dict(fps=f, keys=k, scaffs=s, props=p, ids=kept)
    print(f"{name} parsed: {len(f)}")

comb_fps = T["BACE1"]["fps"] + T["AChE"]["fps"]
comb_keys = set(x for x in T["BACE1"]["keys"] + T["AChE"]["keys"] if x)
comb_scaffs = set(x for x in T["BACE1"]["scaffs"] + T["AChE"]["scaffs"] if x)

print("\n=== 1. DIRECT OVERLAP (InChIKey) ===")
bk = [k for k in b_keys if k]
ov = set(bk) & comb_keys
print(f"B3DB compounds also in target actives: {len(ov)}")
for name in T:
    print(f"  overlap with {name}: {len(set(bk) & set(x for x in T[name]['keys'] if x))}")

print("\n=== 2. B3DB -> nearest target active (how much labeled ground truth is target-like) ===")
maxsim = np.zeros(len(b_fps))
per = {}
for name in T:
    s = np.array([max(DataStructs.BulkTanimotoSimilarity(f, T[name]["fps"])) for f in b_fps])
    per[name] = s
    maxsim = np.maximum(maxsim, s)
print(f"median max-sim: {np.median(maxsim):.3f}   mean: {maxsim.mean():.3f}   p90: {np.percentile(maxsim,90):.3f}   max: {maxsim.max():.3f}")
print(f"{'thresh':>7} {'n':>6} {'BBB+':>6} {'BBB-':>6}   {'BACE1-like':>11} {'AChE-like':>10}")
for t in [0.3,0.35,0.4,0.5,0.6,0.7,0.8]:
    m = maxsim >= t
    print(f"{t:>7} {m.sum():>6} {(labels[m]=='BBB+').sum():>6} {(labels[m]=='BBB-').sum():>6}   {(per['BACE1']>=t).sum():>11} {(per['AChE']>=t).sum():>10}")

print("\n=== 3. Target actives -> nearest B3DB compound (out-of-domain fraction: the paper's premise) ===")
for name in T:
    s = np.array([max(DataStructs.BulkTanimotoSimilarity(f, b_fps)) for f in T[name]["fps"]])
    print(f"{name}: n={len(s)} median={np.median(s):.3f} mean={s.mean():.3f}")
    frac = " ".join(f"<{t}: {100*(s<t).mean():.1f}%" for t in [0.3,0.35,0.4,0.5])
    print(f"   fraction below threshold -> {frac}")

print("\n=== 4. Scaffold overlap (Bemis-Murcko) ===")
bs = set(x for x in b_scaffs if x)
print(f"B3DB scaffolds: {len(bs)}  target scaffolds: {len(comb_scaffs)}  shared: {len(bs & comb_scaffs)}")

print("\n=== 5. Physicochemical space (MW / cLogP / TPSA) ===")
def fmt(p, n): return f"{n:>8}  MW {p[:,0].mean():6.1f}±{p[:,0].std():5.1f}   cLogP {p[:,1].mean():5.2f}±{p[:,1].std():4.2f}   TPSA {p[:,2].mean():6.1f}±{p[:,2].std():5.1f}"
print(fmt(b_props[labels=='BBB+'], "BBB+"))
print(fmt(b_props[labels=='BBB-'], "BBB-"))
for name in T: print(fmt(T[name]["props"], name))
