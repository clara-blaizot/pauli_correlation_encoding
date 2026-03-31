import rustworkx as rx
from rustworkx.visualization import mpl_draw
import networkx as nx
import matplotlib.pyplot as plt


def graph_creation(number_nodes):
    """
    Create a random graph with the given number of nodes and edge probability, 
    and return it as a NetworkX graph.
    
    """

    graph = rx.undirected_gnp_random_graph(number_nodes, probability_of_edge, seed=42)
    mpl_draw(graph)
    plt.show()
    nx_graph = nx.Graph() 
    nx_graph.add_nodes_from(range(number_nodes)) 
    for edge in graph.edge_list():
        nx_graph.add_edge(edge[0], edge[1])
    
    return nx_graph


def tree_creation(number_nodes):
    """
    Create a random tree with the given number of nodes, and return it as a NetworkX graph.
    
    """

    tree = rx.random_tree(number_nodes, seed=42)
    mpl_draw(tree)
    nx_tree = nx.Graph() 
    nx_tree.add_nodes_from(range(number_nodes)) 
    for edge in tree.edge_list():
        nx_tree.add_edge(edge[0], edge[1])
    
    return nx_tree


def instance_creation(num_nodes, problem):
    if problem == "Max-Cut":
        return graph_creation(num_nodes)
    elif problem == "Minimal-Multi-Cut":
        return tree_creation(num_nodes)
    else:
        raise ValueError("Invalid problem type")