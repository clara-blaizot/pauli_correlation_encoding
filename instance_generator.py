
import rustworkx as rx
from rustworkx.visualization import mpl_draw
import networkx as nx
import matplotlib.pyplot as plt


def graph_creation(number_nodes, probability_of_edge):
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

# my_graph = graph_creation(15, 0.3)