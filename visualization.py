import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from collections import Counter


# ============================================================
# STYLE GLOBAL
# ============================================================
COLORS = {
    "classical": "#2563EB",
    "quantum":   "#EA580C",
    "ratio":     "#7C3AED",
    "feasible":  "#16A34A",
    "infeasible":"#DC2626",
    "neutral":   "#64748B",
}

def _setup():
    plt.rcParams.update({
        "figure.dpi":      130,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid":       True,
        "grid.alpha":      0.3,
        "grid.linestyle":  ":",
        "font.size":       11,
    })


# ============================================================
# 1. CONVERGENCE DE L'OPTIMISEUR
# ============================================================

def plot_objective_evolution(history_loss, title="Convergence de l'optimiseur (COBYLA)",
                              save_path=None):
    """
    Trace l'évolution de la loss pendant l'optimisation hybride.
    Répond à : l'algorithme converge-t-il ?
    """
    _setup()
    if not history_loss:
        print("Historique vide.")
        return

    fig, ax = plt.subplots(figsize=(8, 4))
    iters = np.arange(1, len(history_loss) + 1)

    ax.plot(iters, history_loss, color=COLORS["quantum"], linewidth=1.5,
            label="Loss COBYLA")
    ax.axhline(y=min(history_loss), color=COLORS["neutral"], linestyle="--",
               linewidth=1, label=f"Min = {min(history_loss):.4f}")

    ax.set_xlabel("Itération")
    ax.set_ylabel("Valeur de la fonction de coût")
    ax.set_title(title)
    ax.legend(framealpha=0.5)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    plt.show()


# ============================================================
# 2. SCALING : PERFORMANCE EN FONCTION DE LA TAILLE
# ============================================================

def plot_performance_scaling(instance_sizes, classical_values, quantum_values,
                              metric_name="Valeur objectif (Cut Size)",
                              problem_type="Max-Cut", save_path=None):
    """
    Courbe de scaling : classique vs quantique en fonction de m.
    Répond à : comment évolue la qualité avec la taille de l'instance ?
    """
    _setup()
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(instance_sizes, classical_values, marker='o', color=COLORS["classical"],
            linewidth=2, label="Classique (one-exchange)")
    ax.plot(instance_sizes, quantum_values, marker='s', linestyle='--',
            color=COLORS["quantum"], linewidth=2, label="Quantique (PCE)")

    ax.set_xlabel("Taille de l'instance (nombre de noeuds m)")
    ax.set_ylabel(metric_name)
    ax.set_title(f"Scaling des performances — {problem_type}")
    ax.legend()

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    plt.show()


# ============================================================
# 3. RATIO D'APPROXIMATION EN FONCTION DE LA TAILLE
# ============================================================

def plot_approximation_ratio_scaling(instance_sizes, approx_ratios,
                                      problem_type="Max-Cut", save_path=None):
    """
    Évolution du ratio rho(x) = f(x)/f(x*) avec la taille.
    Répond à : la qualité se dégrade-t-elle avec m ?
    """
    _setup()
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(instance_sizes, approx_ratios, marker='^', color=COLORS["ratio"],
            linewidth=2, label="Ratio d'approximation rho(x)")
    ax.axhline(y=1.0, color=COLORS["classical"], linestyle="-", linewidth=1.2,
               alpha=0.6, label="Optimum (rho = 1.0)")
    ax.axhline(y=0.941, color=COLORS["neutral"], linestyle=":", linewidth=1.2,
               alpha=0.8, label="Seuil NP-dur (0.941)")

    if problem_type == "Max-Cut":
        ax.set_ylim(0.0, 1.15)

    ax.set_xlabel("Taille de l'instance (nombre de noeuds m)")
    ax.set_ylabel("Ratio d'approximation rho(x)")
    ax.set_title(f"Qualité d'approximation en fonction de m — {problem_type}")
    ax.legend()

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    plt.show()


# ============================================================
# 4. HISTOGRAMME DES ÉNERGIES ÉCHANTILLONNÉES
# ============================================================

def plot_energy_histogram(energy_values, optimal_energy=None,
                           title="Distribution des énergies échantillonnées",
                           save_path=None):
    """
    Histogramme de la distribution des énergies sur plusieurs runs.
    Répond à : le solveur quantique trouve-t-il souvent l'optimum ?
    """
    _setup()
    fig, ax = plt.subplots(figsize=(7, 4))

    n_bins = max(10, len(energy_values) // 5)
    ax.hist(energy_values, bins=n_bins, color=COLORS["quantum"],
            edgecolor="white", linewidth=0.5, alpha=0.85, label="Énergies observées")

    if optimal_energy is not None:
        ax.axvline(x=optimal_energy, color=COLORS["classical"], linewidth=2,
                   linestyle="--", label=f"Référence classique = {optimal_energy:.2f}")

    ax.set_xlabel("Valeur de l'énergie (objectif)")
    ax.set_ylabel("Nombre de runs")
    ax.set_title(title)
    ax.legend()

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    plt.show()


# ============================================================
# 5. PROBABILITÉS DES BITSTRINGS DOMINANTS
# ============================================================

def plot_bitstring_probabilities(bitstrings_list, top_k=15,
                                  title="Configurations les plus fréquentes",
                                  save_path=None):
    """
    Barplot des top_k bitstrings les plus fréquemment retournés.
    Répond à : quelles configurations dominent la sortie du solveur ?

    Args:
        bitstrings_list : liste de tuples ou de strings représentant les bitstrings
    """
    _setup()
    counts = Counter(
        tuple(b) if not isinstance(b, str) else b
        for b in bitstrings_list
    )
    total = sum(counts.values())
    top = counts.most_common(top_k)
    labels = ["".join(str(b) for b in k) for k, _ in top]
    probs  = [v / total for _, v in top]

    fig, ax = plt.subplots(figsize=(max(8, len(labels) * 0.6), 4))
    bars = ax.bar(range(len(labels)), probs, color=COLORS["quantum"],
                  edgecolor="white", linewidth=0.5)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_xlabel("Bitstring")
    ax.set_ylabel("Probabilité observée")
    ax.set_title(title)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    plt.show()


# ============================================================
# 6. TAUX DE FAISABILITÉ
# ============================================================

def plot_feasibility_rate(instance_sizes, feasibility_rates,
                           problem_type="Max-Cut", save_path=None):
    """
    Taux de solutions réalisables en fonction de la taille de l'instance.
    Répond à : l'encodage reste-t-il valide quand m augmente ?
    """
    _setup()
    fig, ax = plt.subplots(figsize=(7, 4))

    ax.plot(instance_sizes, [r * 100 for r in feasibility_rates],
            marker='D', color=COLORS["feasible"], linewidth=2,
            label="Taux de faisabilité (%)")
    ax.axhline(y=100, color=COLORS["neutral"], linestyle=":", linewidth=1)
    ax.set_ylim(0, 110)
    ax.set_xlabel("Taille de l'instance (nombre de noeuds m)")
    ax.set_ylabel("Solutions réalisables (%)")
    ax.set_title(f"Taux de faisabilité en fonction de m — {problem_type}")
    ax.legend()

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    plt.show()


# ============================================================
# 7. TABLEAU DE BORD COMPLET (figure multi-panneaux)
# ============================================================

def plot_dashboard(history_loss, instance_sizes, classical_values,
                   quantum_values, approx_ratios, energy_values=None,
                   classical_objective=None, problem_type="Max-Cut",
                   save_path=None):
    """
    Figure multi-panneaux pour la soutenance.
    Regroupe convergence + scaling + ratio + histogramme en un seul graphique.
    """
    _setup()
    has_hist = energy_values is not None and len(energy_values) > 0
    n_cols = 2
    n_rows = 2 if has_hist else 2

    fig = plt.figure(figsize=(14, 9))
    fig.suptitle(f"Tableau de bord — Solveur PCE — {problem_type}",
                 fontsize=14, fontweight="normal", y=1.01)
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    # --- Panneau 1 : Convergence ---
    ax1 = fig.add_subplot(gs[0, 0])
    iters = np.arange(1, len(history_loss) + 1)
    ax1.plot(iters, history_loss, color=COLORS["quantum"], linewidth=1.5)
    ax1.axhline(min(history_loss), color=COLORS["neutral"], linestyle="--",
                linewidth=1, alpha=0.7)
    ax1.set_xlabel("Itération")
    ax1.set_ylabel("Loss")
    ax1.set_title("Convergence de l'optimiseur")
    ax1.grid(True, linestyle=":", alpha=0.3)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # --- Panneau 2 : Scaling objectif ---
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(instance_sizes, classical_values, marker='o', color=COLORS["classical"],
             linewidth=2, label="Classique")
    ax2.plot(instance_sizes, quantum_values, marker='s', linestyle='--',
             color=COLORS["quantum"], linewidth=2, label="Quantique (PCE)")
    ax2.set_xlabel("Taille m (noeuds)")
    ax2.set_ylabel("Valeur objectif")
    ax2.set_title("Scaling des performances")
    ax2.legend(fontsize=9)
    ax2.grid(True, linestyle=":", alpha=0.3)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # --- Panneau 3 : Ratio d'approximation ---
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(instance_sizes, approx_ratios, marker='^', color=COLORS["ratio"],
             linewidth=2, label="rho(x)")
    ax3.axhline(1.0, color=COLORS["classical"], linestyle="-",
                linewidth=1, alpha=0.6, label="Optimal")
    ax3.axhline(0.941, color=COLORS["neutral"], linestyle=":",
                linewidth=1, alpha=0.7, label="Seuil 0.941")
    ax3.set_ylim(0, 1.15)
    ax3.set_xlabel("Taille m (noeuds)")
    ax3.set_ylabel("Ratio rho(x)")
    ax3.set_title("Qualité d'approximation")
    ax3.legend(fontsize=9)
    ax3.grid(True, linestyle=":", alpha=0.3)
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)

    # --- Panneau 4 : Histogramme ou message ---
    ax4 = fig.add_subplot(gs[1, 1])
    if has_hist:
        n_bins = max(10, len(energy_values) // 5)
        ax4.hist(energy_values, bins=n_bins, color=COLORS["quantum"],
                 edgecolor="white", linewidth=0.5, alpha=0.85)
        if classical_objective is not None:
            ax4.axvline(classical_objective, color=COLORS["classical"],
                        linewidth=2, linestyle="--",
                        label=f"Classique = {classical_objective:.1f}")
            ax4.legend(fontsize=9)
        ax4.set_xlabel("Valeur objectif")
        ax4.set_ylabel("Nombre de runs")
        ax4.set_title("Distribution des énergies")
    else:
        # Stats textuelles si pas d'histogramme
        stats_text = (
            f"Taille max testée : m = {max(instance_sizes)}\n\n"
            f"Ratio final       : {approx_ratios[-1]:.3f}\n\n"
            f"Ratio moyen       : {np.mean(approx_ratios):.3f}\n\n"
            f"Ratio min         : {min(approx_ratios):.3f}"
        )
        ax4.text(0.5, 0.5, stats_text, transform=ax4.transAxes,
                 fontsize=12, va="center", ha="center",
                 bbox=dict(boxstyle="round,pad=0.5",
                           facecolor="whitesmoke", edgecolor="lightgray"))
        ax4.set_title("Résumé statistique")
        ax4.axis("off")

    ax4.grid(True, linestyle=":", alpha=0.3)
    ax4.spines["top"].set_visible(False)
    ax4.spines["right"].set_visible(False)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")
    plt.show()