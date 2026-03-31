import networkx as nx

def classical_solver(instance , problem_type):
    """
    Résout un problème d'optimisation sur un graphe NetworkX via des algorithmes classiques.
    
    Arguments:
        nx_graph: Le graphe NetworkX (instance du problème).
        problem_type: "Max-cut" ou "Minimal-Multi-Cut".
        
    Returns:
        Si Max-cut : (cut_size, partition)
        Si Minimal-Multi-Cut : (cut_size, cut_edges)
    """
    
    if problem_type == "Max-Cut":
        # Heuristique de recherche locale (One-Exchange) 
        # On fixe le seed pour la reproductibilité exigée par le framework 
        curr_cut_size, partition = nx.approximation.one_exchange(instance, seed=1)
        print(f"Cut size: {curr_cut_size}")
        print(f"Partition 1: {partition[0]}")
        print(f"Partition 2: {partition[1]}")
        return curr_cut_size, partition

    elif problem_type == "Minimal-Multi-Cut":
        # Pour le Multi-cut, on cherche à minimiser le poids des arêtes supprimées 
        # NetworkX utilise une approximation basée sur les coupes minimales isolantes
        # Note : Cette fonction nécessite souvent des capacités de noeuds (capacities)
        cut_edges = nx.approximation.minimum_node_cut(instance)
        cut_size = len(cut_edges)
        print(f"Cut size: {cut_size}")
        print(f"Cut edges: {cut_edges}")
        return cut_size, cut_edges

    else:
        raise ValueError("Type de problème non supporté. Choisissez 'Max-cut' ou 'Minimal-Multi-Cut'.")