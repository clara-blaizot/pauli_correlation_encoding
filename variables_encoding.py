
from itertools import combinations 
from qiskit.quantum_info import SparsePauliOp


def build_pauli_correlation_encoding(pauli, node_list, n, k=2):
    """

    Args:
        pauli (str): X, Y ou Z 
        node_list (list): liste des noeuds encodés sur la matrice de Pauli étudiée
        n (int): nombre de qubits
        k (int, optional): taux de compression 

    Returns:
        hamiltonian (list): La liste des opérateurs hamiltoniens pour le type de Pauli donné
    """
    pauli_correlation_encoding = []
    for idx, c in enumerate(combinations(range(n), k)):      # Generate all combinations of qubits for the given k
        if idx >= len(node_list):      # Only consider combinations up to the length of the node list
            break
        paulis = ["I"] * n          # Initialize all qubits to identity
        paulis[c[0]], paulis[c[1]] = pauli, pauli    # Set the specified Pauli operator on the selected qubits
        pauli_correlation_encoding.append(("".join(paulis)[::-1], 1))    # Append the Pauli string to the encoding list

    hamiltonian = []
    for pauli, weight in pauli_correlation_encoding:
        hamiltonian.append(SparsePauliOp.from_list([(pauli, weight)]))

    return hamiltonian



def variables_encoding(number_nodes, number_qubits):
    """

    Args:
        number_nodes (int): nombre de noeuds du graphe 
        number_qubits (int): nombre de qubits utilisés pour l'encodage 

    Returns:
        list: La liste des opérateurs hamiltoniens pour chaque type de Pauli
    """

    list_size = number_nodes // 3
    node_x = [i for i in range(list_size)]
    node_y = [i for i in range(list_size, 2 * list_size)]
    node_z = [i for i in range(2 * list_size, number_nodes)]

    print("List 1:", node_x)
    print("List 2:", node_y)
    print("List 3:", node_z)
    
    hamiltonian = [build_pauli_correlation_encoding("X", node_x, number_qubits), build_pauli_correlation_encoding("Y", node_y, number_qubits), build_pauli_correlation_encoding("Z", node_z, number_qubits)]
    return hamiltonian

