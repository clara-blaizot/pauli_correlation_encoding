import networkx as nx
import numpy as np  


def calc_cut_size(graph, partition0, partition1):
    """Calculate the cut size of the given partitions of the graph."""

    cut_size = 0
    for edge0, edge1 in graph.edges():
        if edge0 in partition0 and edge1 in partition1:
            cut_size += 1
        elif edge0 in partition1 and edge1 in partition0:
            cut_size += 1
    return cut_size


def decode_bits_from_expectations(exp_map):
    """
    Décode un dictionnaire {noeud: <Pi>} en liste de bits ordonnée.
    xi = 1 si <Pi> >= 0, xi = 0 sinon.
    """
    n = len(exp_map)
    bits = []
    for i in range(n):
        bits.append(1 if exp_map[i] >= 0 else 0)
    return bits


def bits_to_partitions(bits):
    """
    Convertit une liste de bits en deux ensembles (partition0, partition1).
    """
    par0, par1 = set(), set()
    for i, b in enumerate(bits):
        if b == 1:
            par0.add(i)
        else:
            par1.add(i)
    return par0, par1


def bit_swap_search(exp_map, graph):
    """
    Recherche locale par single-bit flip (O(|E|) comme dans Sciorilli et al.).

    L'algorithme de l'article fait un seul passage séquentiel :
    pour chaque noeud i, on flip xi et on garde le changement
    si la valeur de coupe s'améliore.

    Args:
        exp_map : dict {node_index: expectation_value <Pi>}
        graph   : graphe NetworkX

    Returns:
        best_cut  : int/float, valeur de la meilleure coupe trouvée
        best_bits : list, bits après optimisation
        par0, par1: sets, les deux partitions finales
    """
    # Décodage initial depuis les espérances
    bits = decode_bits_from_expectations(exp_map)
    nodes = sorted(graph.nodes())

    # Calcul initial de la coupe
    par0, par1 = bits_to_partitions(bits)
    current_cut = calc_cut_size(graph, par0, par1)

    # Single-bit flip séquentiel (un seul passage, O(m) total)
    for i in nodes:
        if i >= len(bits):
            continue

        # Flip du bit i
        bits[i] = 1 - bits[i]
        par0_new, par1_new = bits_to_partitions(bits)
        new_cut = calc_cut_size(graph, par0_new, par1_new)

        if new_cut > current_cut:
            # On garde le flip
            current_cut = new_cut
            par0, par1 = par0_new, par1_new
        else:
            # On annule le flip
            bits[i] = 1 - bits[i]

    return current_cut, bits, par0, par1