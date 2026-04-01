import numpy as np
import networkx as nx

# ==========================================
# 1. CALCUL DE L'OBJECTIF SPÉCIFIQUE
# ==========================================

def calculate_maxcut_value(graph, quantum_result_dict):
    """
    Calcule l'objectif f(x) pour Max-Cut (à maximiser).
    L'objectif est la somme des poids des arêtes reliant deux partitions différentes.
    """
    par0 = quantum_result_dict.get("par0", set())
    par1 = quantum_result_dict.get("par1", set())
    cut_value = 0
    
    for u, v in graph.edges():
        if (u in par0 and v in par1) or (u in par1 and v in par0):
            weight = graph[u][v].get('weight', 1.0)
            cut_value += weight
            
    return cut_value

def calculate_min_multicut_value(graph, quantum_result_dict):
    """
    Calcule l'objectif f(x) pour Minimal-Multi-Cut (à minimiser).
    L'objectif est la somme des poids des arêtes qui ont été coupées pour séparer les terminaux.
    """
    # On suppose ici que le solveur quantique retourne la liste des arêtes coupées
    cut_edges = quantum_result_dict.get("cut_edges", [])
    cut_value = 0
    
    for u, v in cut_edges:
        # On vérifie que l'arête existe bien dans le graphe d'origine par sécurité
        if graph.has_edge(u, v):
            weight = graph[u][v].get('weight', 1.0)
            cut_value += weight
            
    return cut_value

def get_objective_value(graph, quantum_result_dict, problem_type):
    """
    Aiguilleur : Appelle la bonne fonction mathématique selon le problème.
    """
    if problem_type == "Max-Cut":
        return calculate_maxcut_value(graph, quantum_result_dict)
    elif problem_type == "Minimal-Multi-Cut":
        return calculate_min_multicut_value(graph, quantum_result_dict)
    else:
        raise ValueError(f"Type de problème non supporté : {problem_type}")


# ==========================================
# 2. MÉTRIQUES ET STATISTIQUES GLOBALES
# ==========================================

def compute_approximation_ratio(quantum_value, classical_value):
    """
    Calcule le ratio d'approximation ρ(x) = f(x) / f(x*).
    """
    if classical_value == 0:
        return 0.0 # Sécurité pour éviter la division par zéro
    
    return quantum_value / classical_value

def compute_trial_statistics(values_list, problem_type):
    """
    Calcule les statistiques sur des essais répétés (obligatoire pour les algos stochastiques).
    Adapte la notion de "meilleur/pire" selon le type d'optimisation (Min ou Max).
    """
    if not values_list:
        return {}

    stats = {
        "mean": np.mean(values_list),
        "std_dev": np.std(values_list),
        "median": np.median(values_list),
    }
    
    if problem_type == "Max-Cut":
        stats["best"] = np.max(values_list)
        stats["worst"] = np.min(values_list)
    elif problem_type == "Minimal-Multi-Cut":
        stats["best"] = np.min(values_list)
        stats["worst"] = np.max(values_list)
        
    return stats

def extract_hybrid_resources(quantum_result_dict, quantum_circuit=None):
    """
    Extrait les métriques de ressources matérielles et logicielles.
    """
    resources = {}
    
    # Nombre d'itérations de l'optimiseur classique
    if "result" in quantum_result_dict:
        resources["optimizer_iterations"] = quantum_result_dict["result"].nfev
    elif "history" in quantum_result_dict:
        resources["optimizer_iterations"] = len(quantum_result_dict["history"]["loss"])
        
    # Profondeur du circuit (si le circuit transpilé est fourni)
    if quantum_circuit is not None:
        resources["circuit_depth"] = quantum_circuit.depth()
        
    return resources


# ==========================================
# 3. FONCTION PRINCIPALE D'ORCHESTRATION
# ==========================================

def compare_solvers(graph, classical_objective, quantum_result_dict, problem_type, quantum_circuit=None):
    """
    Génère un rapport comparatif standardisé, peu importe le problème.
    C'est la fonction à appeler dans main_workflow.ipynb.
    """
    # 1. Calcul de l'objectif quantique via l'aiguilleur
    quantum_objective = get_objective_value(graph, quantum_result_dict, problem_type)
    
    # 2. Calcul du ratio d'approximation [cite: 152]
    approx_ratio = compute_approximation_ratio(quantum_objective, classical_objective)
    
    # 3. Extraction des métriques de coût [cite: 143]
    resources = extract_hybrid_resources(quantum_result_dict, quantum_circuit)
    
    # Construction du dictionnaire de rapport [cite: 24, 143]
    report = {
        "problem_type": problem_type,
        "classical_objective": classical_objective,
        "quantum_objective": quantum_objective,
        "approximation_ratio": approx_ratio,
        "optimizer_iterations": resources.get("optimizer_iterations", None),
        "circuit_depth": resources.get("circuit_depth", None)
    }
    
    return report


'''Ce dont il y a besoin en paramètres d'entrées, à mettre dans le notebook main'''
# # 1. Génération de l'instance (via ton module instance_generator.py)
# # graph = generate_my_graph(...) 

# # 2. Résolution Classique
# classical_cut_size, _ = classical_solver(graph, "Max-Cut")

# # 3. Résolution Quantique
# quantum_result = solve_maxcut_pce(num_qubits=len(graph.nodes), pce_groups=mes_groupes, instance=graph)

# # 4. Calcul des Métriques (C'est ici que tu utilises metrics.py !)
# report = compare_solvers_maxcut(graph, classical_cut_size, quantum_result)

# print(f"Objectif classique : {report['classical_objective']}")
# print(f"Objectif quantique : {report['quantum_objective']}")
# print(f"Ratio d'approximation : {report['approximation_ratio']}")