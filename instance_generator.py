import rustworkx as rx
from rustworkx.visualization import mpl_draw
import networkx as nx
import matplotlib.pyplot as plt


def graph_creation(number_nodes):
    """
    Create a random graph with the given number of nodes and edge probability, 
    and return it as a NetworkX graph.
    
    """

    graph = rx.undirected_gnp_random_graph(number_nodes, 0.5, seed=42)
    nx_graph = nx.Graph() 
    nx_graph.add_nodes_from(range(number_nodes)) 
    for edge in graph.edge_list():
        nx_graph.add_edge(edge[0], edge[1])
    
    return nx_graph


def tree_creation(number_nodes, num_pairs=3):
    """
    Crée un arbre aléatoire via NetworkX (stable) et le convertit pour Rustworkx.
    """
    # 1. Création de l'arbre avec NetworkX (Garanti sans erreur d'import)
    nx_tree = nx.random_tree(number_nodes, seed=42)
    
    # 2. Conversion vers Rustworkx (si tes autres fonctions en ont besoin)
    # On reconstruit le graphe rx à partir des arêtes de nx
    rx_tree = rx.PyGraph()
    rx_tree.add_nodes_from(range(number_nodes))
    rx_tree.add_edges_from([(u, v, None) for u, v in nx_tree.edges()])
    
    # 3. Génération des paires (S, T) aléatoires
    rng = np.random.default_rng(seed=42)
    sources = []
    terminals = []
    
    nodes = list(range(number_nodes))
    for _ in range(num_pairs):
        # On choisit deux nœuds distincts
        pair = rng.choice(nodes, size=2, replace=False)
        sources.append(int(pair[0]))
        terminals.append(int(pair[1]))
    
    # Retourne les deux versions du graphe et les paires
    # Tu peux adapter selon ce que ton notebook attend
    return nx_tree, sources, terminals


def instance_creation(num_nodes, problem):
    if problem == "Max-Cut":
        return graph_creation(num_nodes)
    elif problem == "Minimal-Multi-Cut":
        return tree_creation(num_nodes)
    else:
        raise ValueError("Invalid problem type")