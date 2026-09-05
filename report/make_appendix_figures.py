"""Generate appendix figures for the NeurIPS manuscript from report/README.md data.

Style: fontsize 14/15, no titles, clean booktabs-like aesthetics.
Outputs into overleaf/figures/.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "overleaf", "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.size": 14,
    "axes.labelsize": 15,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 14,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 200,
})

MODELS = ["gpt5-6sol", "opus5", "llama3-3", "qwen3-8", "deepseek"]
LABELS = ["GPT-5.6", "Opus 5", "Llama 3.3", "Qwen 3.8", "DeepSeek"]


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


# ---------------- 1. Toy track: Lane-2 combined F1 per case ----------------
toy_cases = ["T1.1", "T1.2", "T2.1", "T2.2", "T3.1", "T3.2", "T4.1", "T4.2", "T4.3", "T4.4"]
toy_comb = [1.00, 1.00, 0.78, 0.68, 1.00, 0.75, 1.00, 1.00, 0.96, 1.00]
fig, ax = plt.subplots(figsize=(7.6, 3.2))
ax.bar(toy_cases, toy_comb, color="#4C72B0")
ax.set_ylabel("Lane-2 combined F1")
ax.set_ylim(0, 1.15)
ax.axhline(1.0, color="grey", lw=0.8, ls="--")
for xx, v in zip(toy_cases, toy_comb):
    ax.text(xx, v + 0.02, f"{v:.2f}", ha="center", fontsize=14)
save(fig, "toy_comb_f1.png")

# ---------------- 2. Game track: per-model aggregate ----------------
g_cov = [0.94, 0.91, 0.89, 0.86, 0.78]
g_comb = [0.79, 0.52, 0.75, 0.82, 0.71]
x = np.arange(len(MODELS)); w = 0.38
fig, ax = plt.subplots(figsize=(7.6, 3.4))
ax.bar(x - w/2, g_cov, w, label="L2 coverage", color="#4C72B0")
ax.bar(x + w/2, g_comb, w, label="L2 combined F1", color="#DD8452")
ax.set_xticks(x); ax.set_xticklabels(LABELS)
ax.set_ylabel("Score"); ax.set_ylim(0, 1.1)
ax.legend(frameon=False, ncol=2)
save(fig, "game_per_model.png")

# ---------------- 3. Game track: model x case combined-F1 heatmap ----------------
game_comb = np.array([
    [0.82, 0.21, 0.82, 1.00, 0.97, 0.28, 1.00, 1.00, 0.97],
    [0.79, 0.10, 0.69, 0.46, 0.87, 0.11, 0.62, 0.35, 0.68],
    [0.89, 0.36, 0.79, 1.00, 0.71, 0.72, 1.00, 0.59, 0.68],
    [0.93, 0.18, 0.88, 0.96, 0.95, 0.74, 0.86, 0.93, 0.96],
    [0.82, 0.15, 0.61, 0.98, 0.95, 0.39, 0.79, 0.86, 0.81],
])
fig, ax = plt.subplots(figsize=(8.6, 3.0))
im = ax.imshow(game_comb, cmap="viridis", vmin=0, vmax=1, aspect="auto")
ax.set_xticks(range(9)); ax.set_xticklabels([f"G{i}" for i in range(1, 10)])
ax.set_yticks(range(5)); ax.set_yticklabels(LABELS)
for i in range(5):
    for j in range(9):
        ax.text(j, i, f"{game_comb[i, j]:.2f}", ha="center", va="center",
                color="white" if game_comb[i, j] < 0.55 else "black", fontsize=14)
cbar = fig.colorbar(im, ax=ax, pad=0.02); cbar.set_label("L2 combined F1", fontsize=15)
save(fig, "game_model_case_heatmap.png")

# ---------------- 4. Situational artifacts heatmap ----------------
situ = np.array([
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3],
    [3, 3, 3, 6, 4, 4, 4, 3, 5, 3, 6],
    [5, 5, 8, 7, 3, 6, 3, 5, 5, 3, 5],
    [4, 3, 8, 4, 4, 5, 6, 4, 4, 6, 5],
])
fig, ax = plt.subplots(figsize=(9.2, 3.0))
im = ax.imshow(situ, cmap="Blues", vmin=0, vmax=8, aspect="auto")
ax.set_xticks(range(11)); ax.set_xticklabels([f"S{i}" for i in range(1, 12)])
ax.set_yticks(range(5)); ax.set_yticklabels(LABELS)
for i in range(5):
    for j in range(11):
        ax.text(j, i, str(situ[i, j]), ha="center", va="center", fontsize=14)
cbar = fig.colorbar(im, ax=ax, pad=0.02); cbar.set_label("Artifacts", fontsize=15)
save(fig, "situational_artifacts.png")

# ---------------- 5. Cultural: L2 combined F1 by model and condition ----------------
comb_ano = [0.639, 0.645, 0.419, 0.686, 0.678]
comb_loc = [0.578, 0.655, 0.398, 0.543, 0.667]
fig, ax = plt.subplots(figsize=(7.6, 3.4))
ax.bar(x - w/2, comb_ano, w, label="Anonymized location", color="#4C72B0")
ax.bar(x + w/2, comb_loc, w, label="Country named", color="#DD8452")
ax.set_xticks(x); ax.set_xticklabels(LABELS)
ax.set_ylabel("Lane-2 combined F1"); ax.set_ylim(0, 0.85)
ax.legend(frameon=False, ncol=2)
save(fig, "cultural_comb_condition.png")

# ---------------- 6. Cultural: location effect deltas ----------------
d_sem = [-0.006, -0.007, -0.001, -0.019, -0.011]
d_comb = [-0.061, 0.010, -0.021, -0.144, -0.011]
fig, ax = plt.subplots(figsize=(7.6, 3.4))
ax.bar(x - w/2, d_sem, w, label=r"$\Delta$ Semantic", color="#55A868")
ax.bar(x + w/2, d_comb, w, label=r"$\Delta$ L2 combined F1", color="#C44E52")
ax.axhline(0, color="black", lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(LABELS)
ax.set_ylabel("With-location minus anonymized")
ax.legend(frameon=False, ncol=2)
save(fig, "cultural_location_delta.png")

# ---------------- 7. Cultural: per-case semantic matrix heatmap ----------------
# Rows = models (Y-axis), columns = cases C1-C14 (X-axis). Order matches LABELS.
sem = np.array([
    #              C1     C2     C3     C4     C5     C6     C7     C8     C9     C10    C11    C12    C13    C14
    [0.913, 0.949, 0.817, 0.913, 0.957, 0.957, 0.926, 0.964, 0.935, 0.886, 0.964, 0.964, 1.000, 0.964],  # GPT-5.6
    [0.817, 0.894, 0.866, 0.764, 0.817, 0.764, 0.707, 0.802, 0.866, 0.886, 0.845, 0.886, 0.791, 0.926],  # Opus 5
    [0.957, 0.949, 0.866, 0.866, 1.000, 0.817, 1.000, 0.802, 0.935, 0.802, 0.886, 0.926, 0.968, 0.926],  # Llama 3.3
    [0.913, 0.949, 0.866, 0.913, 0.957, 0.913, 0.964, 0.964, 0.935, 0.886, 0.964, 0.845, 0.935, 0.926],  # Qwen 3.8
    [0.913, 0.894, 0.854, 0.764, 0.913, 0.957, 0.707, 0.845, 0.866, 0.964, 0.802, 0.905, 1.000, 0.802],  # DeepSeek
])
fig, ax = plt.subplots(figsize=(11.5, 3.4))
cmap = plt.cm.viridis.copy(); cmap.set_bad("lightgrey")
im = ax.imshow(sem, cmap=cmap, vmin=0.6, vmax=1.0, aspect="auto")
ax.set_xticks(range(14)); ax.set_xticklabels([f"C{i}" for i in range(1, 15)])
ax.set_yticks(range(5)); ax.set_yticklabels(LABELS)
for i in range(5):
    for j in range(14):
        if not np.isnan(sem[i, j]):
            ax.text(j, i, f"{sem[i, j]:.2f}", ha="center", va="center",
                    color="white" if sem[i, j] < 0.85 else "black", fontsize=12)
cbar = fig.colorbar(im, ax=ax, pad=0.02); cbar.set_label("Semantic score", fontsize=15)
save(fig, "cultural_semantic_matrix.png")

print("done")




