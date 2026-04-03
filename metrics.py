import numpy as np
import math


# ============================================================
# 1. CALCUL DE L'OBJECTIF
# ============================================================

def calculate_maxcut_value(graph, result_dict):
    """
    Calcule f(x) pour Max-Cut depuis un dict {par0, par1}.
    """
    par0 = result_dict.get("par0", set())
    par1 = result_dict.get("par1", set())
    cut_value = 0
    for u, v in graph.edges():
        if (u in par0 and v in par1) or (u in par1 and v in par0):
            cut_value += graph[u][v].get('weight', 1.0)
    return cut_value


def calculate_min_multicut_value(graph, result_dict):
    """
    Calcule f(x) pour Minimal-Multi-Cut depuis un dict {cut_edges}.
    """
    cut_edges = result_dict.get("cut_edges", [])
    cut_value = 0
    for u, v in cut_edges:
        if graph.has_edge(u, v):
            cut_value += graph[u][v].get('weight', 1.0)
    return cut_value


def get_objective_value(graph, result_dict, problem_type):
    if problem_type == "Max-Cut":
        return calculate_maxcut_value(graph, result_dict)
    elif problem_type == "Minimal-Multi-Cut":
        return calculate_min_multicut_value(graph, result_dict)
    else:
        raise ValueError(f"Problème non supporté : {problem_type}")


# ============================================================
# 2. MÉTRIQUES INDIVIDUELLES (Section 1.8 du PDF)
# ============================================================

def compute_approximation_ratio(quantum_value, classical_value):
    """
    rho(x) = f(x) / f(x*)
    Pour Max-Cut : ratio <= 1 (plus c'est proche de 1, mieux c'est).
    Pour Min-Multi-Cut : ratio >= 1 (plus c'est proche de 1, mieux c'est).
    """
    if classical_value == 0:
        return 0.0
    return quantum_value / classical_value


def check_feasibility(graph, result_dict, problem_type):
    """
    Vérifie que la solution retournée est réalisable.
    Retourne True/False + un message d'explication.
    """
    if problem_type == "Max-Cut":
        par0 = result_dict.get("par0", set())
        par1 = result_dict.get("par1", set())
        all_nodes = set(graph.nodes())
        covered = par0 | par1
        feasible = (covered == all_nodes) and (par0.isdisjoint(par1))
        msg = "OK" if feasible else f"Noeuds manquants : {all_nodes - covered}"
        return feasible, msg

    elif problem_type == "Minimal-Multi-Cut":
        # On vérifie juste que des arêtes ont été retournées
        cut_edges = result_dict.get("cut_edges", [])
        feasible = len(cut_edges) > 0
        msg = "OK" if feasible else "Aucune arête coupée retournée"
        return feasible, msg

    return False, "Type de problème inconnu"


def compute_time_to_solution(p_success, time_per_run, alpha=0.99):
    """
    TTS_alpha = ceil(log(1-alpha) / log(1-p)) * time_per_run
    (Section 1.8.1 du PDF)

    Args:
        p_success   : probabilité de succès par run (float in (0,1])
        time_per_run: durée d'un run en secondes
        alpha       : niveau de confiance cible (défaut 0.99)

    Returns:
        tts : time to solution en secondes
        n_reps : nombre de répétitions nécessaires
    """
    if p_success <= 0:
        return float('inf'), float('inf')
    if p_success >= 1:
        return time_per_run, 1

    n_reps = math.ceil(math.log(1 - alpha) / math.log(1 - p_success))
    tts = n_reps * time_per_run
    return tts, n_reps


# ============================================================
# 3. STATISTIQUES SUR ESSAIS RÉPÉTÉS (Section 1.8.3 du PDF)
# ============================================================

def compute_trial_statistics(values_list, problem_type):
    """
    Statistiques sur plusieurs essais indépendants.
    Retourne mean, std, median, best, worst.
    """
    if not values_list:
        return {}

    arr = np.array(values_list, dtype=float)
    stats = {
        "mean":    float(np.mean(arr)),
        "std_dev": float(np.std(arr)),
        "median":  float(np.median(arr)),
    }

    if problem_type == "Max-Cut":
        stats["best"]  = float(np.max(arr))
        stats["worst"] = float(np.min(arr))
    elif problem_type == "Minimal-Multi-Cut":
        stats["best"]  = float(np.min(arr))
        stats["worst"] = float(np.max(arr))

    return stats


# ============================================================
# 4. EXTRACTION DES RESSOURCES CIRCUIT
# ============================================================

def extract_hybrid_resources(quantum_result_dict, quantum_circuit=None):
    """
    Extrait les métriques de ressources (iterations optimiseur, profondeur circuit).
    """
    resources = {}

    if "result" in quantum_result_dict:
        resources["optimizer_iterations"] = quantum_result_dict["result"].nfev
    elif "history" in quantum_result_dict:
        resources["optimizer_iterations"] = len(quantum_result_dict["history"]["loss"])

    if quantum_circuit is not None:
        resources["circuit_depth"] = quantum_circuit.depth()
        resources["num_parameters"] = quantum_circuit.num_parameters

    return resources


# ============================================================
# 5. RAPPORT COMPARATIF COMPLET
# ============================================================

def compare_solvers(graph, classical_objective, quantum_result_dict,
                    problem_type, quantum_circuit=None, time_per_run=None):
    """
    Génère un rapport comparatif complet.
    Fonction principale à appeler depuis le notebook.

    Returns:
        report : dict avec tous les indicateurs du PDF
    """
    # Valeur objectif quantique
    quantum_objective = get_objective_value(graph, quantum_result_dict, problem_type)

    # Ratio d'approximation
    approx_ratio = compute_approximation_ratio(quantum_objective, classical_objective)

    # Faisabilité
    feasible, feasibility_msg = check_feasibility(graph, quantum_result_dict, problem_type)

    # Ressources
    resources = extract_hybrid_resources(quantum_result_dict, quantum_circuit)

    # TTS (si temps par run fourni et si on a l'historique pour estimer p_success)
    tts, n_reps = None, None
    if time_per_run is not None:
        # p_success estimée : 1 si le ratio dépasse 0.9, sinon ratio
        p_est = min(1.0, max(1e-6, approx_ratio))
        tts, n_reps = compute_time_to_solution(p_est, time_per_run)

    report = {
        "problem_type":          problem_type,
        "n_nodes":               graph.number_of_nodes(),
        "n_edges":               graph.number_of_edges(),
        "classical_objective":   classical_objective,
        "quantum_objective":     quantum_objective,
        "approximation_ratio":   approx_ratio,
        "feasible":              feasible,
        "feasibility_msg":       feasibility_msg,
        "optimizer_iterations":  resources.get("optimizer_iterations"),
        "circuit_depth":         resources.get("circuit_depth"),
        "num_parameters":        resources.get("num_parameters"),
        "time_per_run_s":        time_per_run,
        "tts_99_s":              tts,
        "n_reps_99":             n_reps,
    }

    return report


def print_report(report):
    """Affiche le rapport de façon lisible dans le notebook."""
    print("=" * 55)
    print(f"  Problème     : {report['problem_type']}")
    print(f"  Graphe       : {report['n_nodes']} noeuds, {report['n_edges']} arêtes")
    print("-" * 55)
    print(f"  Classique    : {report['classical_objective']:.4f}")
    print(f"  Quantique    : {report['quantum_objective']:.4f}")
    print(f"  Ratio rho    : {report['approximation_ratio']:.4f}")
    print(f"  Réalisable   : {report['feasible']}  ({report['feasibility_msg']})")
    print("-" * 55)
    if report['optimizer_iterations'] is not None:
        print(f"  Itérations   : {report['optimizer_iterations']}")
    if report['circuit_depth'] is not None:
        print(f"  Profondeur   : {report['circuit_depth']}")
    if report['tts_99_s'] is not None:
        print(f"  TTS (99%)    : {report['tts_99_s']:.2f} s  ({report['n_reps_99']} runs)")
    print("=" * 55)