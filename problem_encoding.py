import numpy as np
import networkx as nx

def loss_func_estimator_maxcut(x, ansatz, hamiltonian, estimator, graph, num_qubits):
    """
    Calculates the specified loss function for the given ansatz, Hamiltonian, and graph.

    The expectation values of each Pauli string in the Hamiltonian are first obtained
    by running the ansatz on the quantum backend. These expectation values are then
    passed through the nonlinear function tanh(alpha * prod_i). The loss function is
    subsequently computed from these transformed values.
    """
    job = estimator.run(
        [
            (ansatz, hamiltonian[0], x),
            (ansatz, hamiltonian[1], x),
            (ansatz, hamiltonian[2], x),
        ]
    )
    result = job.result()

    # calculate the loss function
    node_exp_map = {}
    idx = 0
    for r in result:
        for ev in r.data.evs:
            node_exp_map[idx] = ev
            idx += 1

    loss = 0
    alpha = num_qubits
    for edge0, edge1 in graph.edge_list(): # graph.edge_list() returns a list of tuples (edge0, edge1) representing the edges of the graph
        loss += np.tanh(alpha * node_exp_map[edge0]) * np.tanh(
            alpha * node_exp_map[edge1]
        )

    regulation_term = 0
    for i in range(len(graph.nodes())):
        regulation_term += np.tanh(alpha * node_exp_map[i]) ** 2
    regulation_term = regulation_term / len(graph.nodes())
    regulation_term = regulation_term**2
    beta = 1 / 2
    v = len(graph.edges()) / 2 + (len(graph.nodes()) - 1) / 4
    regulation_term = beta * v * regulation_term

    loss = loss + regulation_term

    global experiment_result # experiment_result is a global variable that stores the results of each iteration of the optimization process. It is a list of dictionaries, where each dictionary contains the loss value and the corresponding expectation values for each node in the graph.
    print(f"Iter {len(experiment_result)}: {loss}") # print the current iteration number and the corresponding loss value. The iteration number is determined by the length of the experiment_result list, which is incremented after each iteration.
    experiment_result.append({"loss": loss, "exp_map": node_exp_map}) # append a new dictionary to the experiment_result list, containing the current loss value and the corresponding expectation values for each node in the graph. This allows us to track the progress of the optimization process over time and analyze the results after the optimization is complete.
    return loss

def loss_func_estimator_min_multicut(x, ansatz, hamiltonian, estimator, graph, terminal_nodes, num_qubits):
    """
    Similar to loss_func_estimator but adapted for the Restricted Vertex Minimum Multicut problem.
    The loss function includes penalties to ensure that terminal nodes are not cut and that
    the unique path between terminal pairs is severed.
    """
    job = estimator.run(
        [
            (ansatz, hamiltonian[0], x),
            (ansatz, hamiltonian[1], x),
            (ansatz, hamiltonian[2], x),
        ]
    )
    result = job.result()

    # calculate the paths between terminal pairs
    paths = []
    for s,t in terminal_nodes:
        path = nx.shortest_path(graph, source=s, target=t)
        paths.append(path)
    
    # calculate the loss function
    node_exp_map = {}
    idx = 0
    for r in result:
        for ev in r.data.evs:
            node_exp_map[idx] = ev 
            idx += 1
    
    loss = 0
    alpha = num_qubits
    # 1er terme
    for node in graph.node_list():
        loss += (1-np.tanh(alpha * node_exp_map[node]))/2 
        
    # 2e terme
    M1 = len(graph.nodes()) + 1
    for node in terminal_nodes:
        loss += M1 * (1-(1-np.tanh(alpha * node_exp_map[node]))/2 ** 2) 
        
    # 3e terme
    M2 = len(graph.nodes()) + 1
    for path in paths: # paths est une liste de listes, où chaque sous-liste contient les indices des sommets sur le chemin unique reliant une paire de terminaux (s_i, t_i)
        path_survival = 0
        for node in path:
            path_survival += (1 - (1-np.tanh(alpha * node_exp_map[node]))/2) # 1 - x_tilde[node]
        loss += M2 * (path_survival ** 2)
    
    # Regulation 
    regulation_term = 0
    for i in range(len(graph.nodes())):
        regulation_term += np.tanh(alpha * node_exp_map[i]) ** 2
    regulation_term = regulation_term / len(graph.nodes())
    regulation_term = regulation_term**2
    beta = 1 / 2
    v = len(graph.nodes())
    regulation_term = beta * v * regulation_term
    loss += regulation_term
    
    global experiment_result
    print(f"Iter {len(experiment_result)}: {loss}")
    experiment_result.append({"loss": loss, "exp_map": node_exp_map})
    
    return loss
