import numpy as np

from qiskit.circuit.library import EfficientSU2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import Estimator
from scipy.optimize import minimize
import problem_encoding
from problem_encoding import loss_func_estimator_maxcut, loss_func_estimator_mis


def build_pce_circuit(num_qubits, reps=2):
    """
    Crée un circuit variationnel (Ansatz) de type EfficientSU2.
    Optimisé localement pour un simulateur Aer.
    """
    backend = AerSimulator()
    qc = EfficientSU2(num_qubits, ["ry", "rz"], reps=reps, entanglement="linear")
    
    pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
    qc_optimized = pm.run(qc)

    return qc_optimized, backend


def run_pce_optimization(qc, pce_groups, graph, num_qubits, problem_type="Max-Cut", max_iter=10):
    """
    Exécute la boucle d'optimisation hybride sur CPU classique.
    Aiguille vers la bonne Loss selon le problème.
    """
    estimator = Estimator()
    problem_encoding.experiment_result = []
    history = {"loss": []}

    # 2. Aiguilleur de fonction de coût
    def loss_wrapper(params):
        if problem_type == "Max-Cut":
            val = loss_func_estimator_maxcut(params, qc, pce_groups, estimator, graph, num_qubits)
        elif problem_type == "MIS":
            val = loss_func_estimator_mis(params, qc, pce_groups, estimator, graph, num_qubits)
        else:
            raise ValueError(f"Type de problème non supporté: {problem_type}")
            
        history["loss"].append(val)
        return val

    np.random.seed(42)
    initial_params = np.random.rand(qc.num_parameters)
    
    result = minimize(
        loss_wrapper, 
        initial_params, 
        method="COBYLA", 
        options={"maxiter": max_iter}
    )
    
    return result, history


def get_partitions(expectation_values):
    """Décode les résultats pour Max-Cut : xi = sgn(<Pi>)."""
    par0, par1 = set(), set()
    for node_idx, val in expectation_values.items():
        if val >= 0:
            par0.add(node_idx)
        else:
            par1.add(node_idx)
    return par0, par1

# 3. Fonction de décodage spécifique au MIS
def get_independent_set(expectation_values):
    """
    Décode les résultats pour le MIS.
    Dans le PCE, une espérance négative donne un x_tilde proche de 1 (nœud sélectionné).
    """
    independent_set = set()
    for node_idx, val in expectation_values.items():
        if val < 0:
            independent_set.add(node_idx)
    return independent_set


def solve_maxcut_pce(num_qubits, pce_groups, instance, reps=2, max_iter=100):
    """Pipeline complet pour Max-Cut"""
    qc, backend = build_pce_circuit(num_qubits, reps=reps)
    
    result, history = run_pce_optimization(qc, pce_groups, instance, num_qubits, problem_type="Max-Cut", max_iter=max_iter)
    
    estimator = Estimator()
    final_theta = result.x
    all_observables = pce_groups  
    
    job = estimator.run([qc] * len(all_observables), all_observables, [final_theta] * len(all_observables))
    exp_values_list = job.result().values
    
    final_expectations = {i: val for i, val in enumerate(exp_values_list)}
    par0, par1 = get_partitions(final_expectations)
    
    return {
        "par0": par0,
        "par1": par1,
        "history": history,
        "result": result,
        "expectations": final_expectations
    }

# 4. Pipeline complet pour le MIS
def solve_mis_pce(num_qubits, pce_groups, instance, reps=2, max_iter=100):
    """Pipeline complet pour le Maximum Independent Set (MIS)"""
    qc, backend = build_pce_circuit(num_qubits, reps=reps)
    
    result, history = run_pce_optimization(qc, pce_groups, instance, num_qubits, problem_type="MIS", max_iter=max_iter)
    
    estimator = Estimator()
    final_theta = result.x
    all_observables = pce_groups  
    
    job = estimator.run([qc] * len(all_observables), all_observables, [final_theta] * len(all_observables))
    exp_values_list = job.result().values
    
    final_expectations = {i: val for i, val in enumerate(exp_values_list)}
    
    # Décodage MIS
    indep_set = get_independent_set(final_expectations)
    
    return {
        "independent_set": indep_set,
        "history": history,
        "result": result,
        "expectations": final_expectations
    }