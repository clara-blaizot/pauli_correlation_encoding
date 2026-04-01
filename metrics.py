import numpy as np
import networkx as nx

def calculate_maxcut_value(graph, par0, par1):
    """
    Calcule la valeur de la coupe (objectif f(x)) pour une partition donnée.
    Utile car quantum_solvers.py retourne les partitions, mais pas la valeur de la coupe.
    """
    cut_value = 0
    for u, v in graph.edges():
        # Si une arête a un sommet dans par0 et l'autre dans par1, elle est coupée
        if (u in par0 and v in par1) or (u in par1 and v in par0):
            # Prendre en compte le poids si le graphe est pondéré, sinon 1
            weight = graph[u][v].get('weight', 1.0)
            cut_value += weight
    return cut_value

def compute_approximation_ratio(quantum_value, classical_value):
    """
    Calcule le ratio d'approximation ρ(x) = f(x) / f(x*).
    Si on maximise (Max-Cut), la baseline classique (f(x*)) est au dénominateur.
    """
    if classical_value == 0:
        return 0.0 # Éviter la division par zéro
    
    # Pour un problème de maximisation, on veut idéalement que ce ratio s'approche de 1
    rho = quantum_value / classical_value
    return rho

def compute_trial_statistics(values_list):
    """
    Prend une liste de valeurs (ex: les tailles de coupes sur N runs quantiques)
    et retourne les statistiques obligatoires pour les algorithmes stochastiques.
    """
    if not values_list:
        return {}

    return {
        "mean": np.mean(values_list),
        "std_dev": np.std(values_list),
        "median": np.median(values_list),
        "best": np.max(values_list),  # np.max car on est sur du Max-Cut
        "worst": np.min(values_list)
    }

def extract_hybrid_resources(quantum_result_dict, quantum_circuit=None):
    """
    Extrait les métriques de ressources de la boucle hybride et du circuit.
    Prend en entrée le dictionnaire retourné par solve_maxcut_pce.
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

def compare_solvers_maxcut(graph, classical_cut_size, quantum_result_dict): 
    """
    Fonction utilitaire pour générer un rapport complet comparant un run classique et un run quantique.
    """
    # 1. Obtenir la valeur de la coupe quantique
    par0 = quantum_result_dict["par0"]
    par1 = quantum_result_dict["par1"]
    quantum_cut_size = calculate_maxcut_value(graph, par0, par1)
    
    # 2. Calculer l'approximation ratio
    approx_ratio = compute_approximation_ratio(quantum_cut_size, classical_cut_size)
    
    # 3. Extraire les ressources
    resources = extract_hybrid_resources(quantum_result_dict)
    
    # Construction du rapport
    report = {
        "classical_objective": classical_cut_size,
        "quantum_objective": quantum_cut_size,
        "approximation_ratio": approx_ratio,
        "optimizer_iterations": resources.get("optimizer_iterations", None)
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