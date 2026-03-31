# Build the quantum circuit
qc = efficient_su2(num_qubits, ["ry", "rz"], reps=2)    # Create a parameterized quantum circuit with 2 repetitions of Ry and Rz gates

# Optimisation hardware : on optimise la structure du circuit pour le backend cible

pm = generate_preset_pass_manager(optimization_level=3, backend=backend)  # Generate a pass manager with optimization level 3 for the specified backend
# un pass manager est un compilateur
qc = pm.run(qc)   # Optimize the quantum circuit using the pass manager


pce = []
pce.append(
    [op.apply_layout(qc.layout) for op in pauli_correlation_encoding_x]  
)
pce.append(
    [op.apply_layout(qc.layout) for op in pauli_correlation_encoding_y]
)
pce.append(
    [op.apply_layout(qc.layout) for op in pauli_correlation_encoding_z]
) 


# Run the optimization without Session (for open plan)
from qiskit_ibm_runtime import Estimator
estimator = Estimator(backend)  # Use the open plan simulator
experiment_result = []

def loss_func(x):
    return loss_func_estimator(
        x, qc, [pce[0], pce[1], pce[2]], estimator, graph
    )

np.random.seed(42)
initial_params = np.random.rand(qc.num_parameters)
result = minimize(
    loss_func, initial_params, method="COBYLA", options={"maxiter": 10}
    )
print(result)


# Calculate the partitions based on the final expectation values
# If the expectation value is positive, the node belongs to partition 0 (par0)
# Otherwise, the node belongs to partition 1 (par1)

par0, par1 = set(), set()

for i in experiment_result[-1]["exp_map"]:
    if experiment_result[-1]["exp_map"][i] >= 0:
        par0.add(i)
    else:
        par1.add(i)
print(par0, par1)

cut_size = calc_cut_size(graph, par0, par1)
print(f"Cut size: {cut_size}")