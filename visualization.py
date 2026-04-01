import matplotlib.pyplot as plt
import numpy as np

def plot_performance_scaling(instance_sizes, classical_values, quantum_values, metric_name="Objectif (Cut Size)", problem_type="Max-Cut"):
    """
    Trace une courbe de mise à l'échelle (Scaling curve) comparant les performances
    classiques et quantiques en fonction de la taille de l'instance.
    """
    plt.figure(figsize=(10, 6))
    
    # Tracé des courbes
    plt.plot(instance_sizes, classical_values, marker='o', linestyle='-', color='blue', label='Classique (Exact/Heuristique)')
    plt.plot(instance_sizes, quantum_values, marker='s', linestyle='--', color='darkorange', label='Quantique (PCE)')
    
    # Application des règles du framework (Titres, Axes, Légende)
    plt.title(f"Comparaison des performances Classique vs Quantique\nProblème : {problem_type}")
    plt.xlabel("Taille de l'instance (Nombre de nœuds)")
    plt.ylabel(metric_name)
    
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend(loc="best")
    
    # Ajout de contexte en bas du graphique
    plt.figtext(0.5, -0.05, "Comparaison de l'évolution de la valeur d'objectif selon la taille du graphe.", ha="center", fontsize=9, style='italic')
    
    plt.tight_layout()
    plt.show()


def plot_approximation_ratio_scaling(instance_sizes, approx_ratios, problem_type="Max-Cut"):
    """
    Trace l'évolution du ratio d'approximation en fonction de la taille de l'instance.
    Idéal pour évaluer la dégradation des performances quantiques sur de gros graphes.
    """
    plt.figure(figsize=(10, 6))
    
    plt.plot(instance_sizes, approx_ratios, marker='^', color='purple', label="Ratio d'approximation ρ(x)")
    
    # Ligne de référence (Optimalité = 1.0)
    plt.axhline(y=1.0, color='red', linestyle='-', alpha=0.5, label='Optimum Classique (ρ = 1.0)')
    
    plt.title(f"Évolution de la qualité d'approximation\nProblème : {problem_type}")
    plt.xlabel("Taille de l'instance (Nombre de nœuds)")
    plt.ylabel("Ratio d'approximation")
    
    # Si Max-Cut, le ratio est généralement <= 1. On ajuste l'axe Y pour la lisibilité.
    if problem_type == "Max-Cut":
        plt.ylim(0.0, 1.1)
        
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend(loc="best")
    
    plt.tight_layout()
    plt.show()


def plot_objective_evolution(history_loss, title="Convergence de l'optimiseur (COBYLA)"):
    """
    Trace l'évolution de la fonction de coût (Objective evolution plot)
    pendant la boucle d'optimisation classique-quantique.
    """
    if not history_loss:
        print("Aucun historique fourni pour l'affichage.")
        return

    iterations = range(1, len(history_loss) + 1)
    
    plt.figure(figsize=(8, 5))
    plt.plot(iterations, history_loss, marker='.', color='green', label='Valeur de la Loss')
    
    plt.title(title)
    plt.xlabel("Nombre d'itérations")
    plt.ylabel("Valeur de la fonction de coût (Loss)")
    
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend(loc="best")
    
    plt.tight_layout()
    plt.show()