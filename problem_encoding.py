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
    n_obs = len(hamiltonian)
    job = estimator.run([ansatz] * n_obs, hamiltonian, [x] * n_obs)
    result = job.result()
    node_exp_map = {idx: ev for idx, ev in enumerate(result.values)}


    loss = 0
    alpha = num_qubits
    for edge0, edge1 in list(graph.edges):
        loss += np.tanh(alpha * node_exp_map[edge0]) * np.tanh(
            alpha * node_exp_map[edge1]
        )

    regulation_term = 0
    for i in graph.nodes():
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



import numpy as np

def loss_func_estimator_mis(x, ansatz, hamiltonian, estimator, graph, num_qubits):
    """
    Fonction de coût pour le problème du Maximum Independent Set (MIS).
    """
    num_observables = len(hamiltonian)
    circuits = [ansatz] * num_observables
    observables = hamiltonian
    parameter_values = [x] * num_observables

    # Appel correct pour Qiskit Aer Estimator
    job = estimator.run(circuits, observables, parameter_values)
    result = job.result()

    # Récupération des espérances
    node_exp_map = {}
    for idx, ev in enumerate(result.values):
        node_exp_map[idx] = ev

    loss = 0
    alpha = num_qubits
    
    # Helper function pour mapper l'espérance [-1, 1] vers une probabilité de sélection [0, 1]
    def x_tilde(exp_val):
        return (1 - np.tanh(alpha * exp_val)) / 2

    # 1. Terme de récompense (On veut maximiser le nombre de sommets, donc on diminue la loss)
    for node in graph.nodes():
        loss -= x_tilde(node_exp_map[node])
        
    # 2. Terme de pénalité (On pénalise si deux sommets adjacents sont sélectionnés)
    P = 1.15   # Le poids de la pénalité doit être strict (> 1)
    for u, v in graph.edges():
        loss += P * (x_tilde(node_exp_map[u]) * x_tilde(node_exp_map[v]))
        
    # 3. Terme de régulation inhérent au PCE (Force les valeurs extrêmes)
    regulation_term = 0
    for i in graph.nodes():
        regulation_term += np.tanh(alpha * node_exp_map[i]) ** 2
    
    regulation_term = (regulation_term / len(graph.nodes())) ** 2
    beta = 0.5
    v = len(graph.nodes())
    regulation_term = beta * v * regulation_term

    loss += regulation_term

    global experiment_result 
    print(f"Iter {len(experiment_result)}: {loss}") 
    experiment_result.append({"loss": loss, "exp_map": node_exp_map}) 
    
    return loss