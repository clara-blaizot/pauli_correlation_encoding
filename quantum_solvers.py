import numpy as np

from qiskit.circuit.library import EfficientSU2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import Estimator
from scipy.optimize import minimize
from problem_encoding import loss_func_estimator


def build_pce_circuit(num_qubits, reps=2):
    """
    Crée un circuit variationnel (Ansatz) de type EfficientSU2.
    Optimisé localement pour un simulateur Aer.
    """
    # Utilisation d'un simulateur local gratuit au lieu du backend IBM 
    backend = AerSimulator()
    qc = EfficientSU2(num_qubits, ["ry", "rz"], reps=reps, entanglement="linear")
    
    # Compilation locale (Pass Manager)
    pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
    qc_optimized = pm.run(qc)

    return qc_optimized, backend




def run_pce_optimization(qc, pce_groups, graph, max_iter=10):
    """
    Exécute la boucle d'optimisation hybride sur CPU classique.
    """
    # Estimator local 
    estimator = Estimator()
    
    # Historique pour suivre l'évolution 
    history = {"loss": []}

    def loss_wrapper(params):
        val = loss_func_estimator(params, qc, pce_groups, estimator, graph)
        history["loss"].append(val)
        return val

    # Initialisation des paramètres
    np.random.seed(42)
    initial_params = np.random.rand(qc.num_parameters)
    
    # Optimisation via COBYLA (souvent utilisé en NISQ) 
    result = minimize(
        loss_wrapper, 
        initial_params, 
        method="COBYLA", 
        options={"maxiter": max_iter}
    )
    
    return result, history



def get_partitions(expectation_values):
    """
    Décode les résultats : xi = sgn(<Pi>).
    """
    par0, par1 = set(), set()
    # On suit l'encodage PCE : positif -> 1, négatif -> -1 
    for node_idx, val in expectation_values.items():
        if val >= 0:
            par0.add(node_idx)
        else:
            par1.add(node_idx)
    return par0, par1




def solve_maxcut_pce(num_qubits, pce_groups, instance, reps=2, max_iter=100):
    """
    Pipeline complet : 
    1. Build circuit -> 2. Optimize -> 3. Get Final <Pi> -> 4. Decode Partitions
    """
    # 1. Préparation du circuit et du simulateur [cite: 137]
    qc, backend = build_pce_circuit(num_qubits, reps=reps)
    
    # 2. Boucle d'optimisation hybride
    result, history = run_pce_optimization(qc, pce_groups, instance, max_iter=max_iter)
    
    # 3. Calcul des espérances finales <Pi> avec les meilleurs paramètres trouvés 
    # On utilise un Estimator local pour la simulation finale
    estimator = Estimator()
    final_theta = result.x
    
    # On aplatit les groupes PCE pour l'Estimator (X, Y, Z)
    all_observables = [op for group in pce_groups for op in group]
    
    # Calcul des <Pi> sur le simulateur Aer [cite: 106, 145]
    job = estimator.run([qc] * len(all_observables), all_observables, [final_theta] * len(all_observables))
    exp_values_list = job.result().values
    
    # Mapping {Index du Noeud: Valeur <Pi>} [cite: 62, 97]
    final_expectations = {i: val for i, val in enumerate(exp_values_list)}
    
    # 4. Décodage en partitions binaires (sgn(<Pi>)) [cite: 62, 106]
    par0, par1 = get_partitions(final_expectations)
    
    return {
        "par0": par0,
        "par1": par1,
        "history": history,
        "result": result,
        "expectations": final_expectations
    }