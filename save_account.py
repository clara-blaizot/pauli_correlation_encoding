# Save your account credentials
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    token="85laRiOzJ_TOfrX4IbUGDuIk49o9SmLQP8d5BMxSbnlj",
    instance="test_instance", 
    channel="ibm_quantum_platform",
    set_as_default=True ,
    overwrite=True
)