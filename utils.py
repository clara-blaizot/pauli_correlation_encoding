def calc_cut_size(graph, partition0, partition1):
    """Calculate the cut size of the given partitions of the graph."""

    cut_size = 0
    for edge0, edge1 in graph.edge_list():
        if edge0 in partition0 and edge1 in partition1:
            cut_size += 1
        elif edge0 in partition1 and edge1 in partition0:
            cut_size += 1
    return cut_size



def bit_swap(experiment_result, graph):
    best_bits = []
    cur_bits = []

    for i in experiment_result[-1]["exp_map"]:
        if experiment_result[-1]["exp_map"][i] >= 0:
            cur_bits.append(1)
        else:
            cur_bits.append(0)
    print(cur_bits)
    
    # Swap the partitions and calculate the cut size
    best_cut = 0
    for edge0, edge1 in graph.edge_list():
        swapped_bits = cur_bits.copy()
        swapped_bits[edge0], swapped_bits[edge1] = (
            swapped_bits[edge1],
            swapped_bits[edge0],
        )

        cur_partition = [set(), set()]
        for i, bit in enumerate(swapped_bits):
            if bit > 0:
                cur_partition[0].add(i)
            else:
                cur_partition[1].add(i)
        cut_size = calc_cut_size(graph, cur_partition[0], cur_partition[1])
        if best_cut < cut_size:
            best_cut = cut_size
            best_bits = swapped_bits

    return(best_cut, best_bits)



