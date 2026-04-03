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

    elif problem_type == "Maximal-Independent-Set":
        # Pour le problème du Maximum Independent Set, on utilise une heuristique de recherche locale
        # Note : NetworkX n'a pas de fonction prête pour ce problème, donc on implémente une heuristique simple
        independent_set = nx.approximation.maximum_independent_set(instance, seed=1)
        print(f"Independent set: {independent_set}")
        return len(independent_set), independent_set

    else:
        raise ValueError("Type de problème non supporté. Choisissez 'Max-cut' ou 'Minimal-Multi-Cut'.")