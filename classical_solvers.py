import networkx as nx


def classical_solver(nx_graph):
    """
    Solve the Max-Cut problem on the given NetworkX graph using a classical approximation algorithm.
    
    Returns the cut size and the partition of the nodes.
    """
    curr_cut_size, partition = nx.approximation.one_exchange(nx_graph, seed=1) # Initial partition using one-exchange heuristic
    return curr_cut_size, partition