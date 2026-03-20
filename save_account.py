# Save your account credentials
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    token="doDq0pH7IpF_Y94_xodH3f905GF2gs1REURbzc9rEVZU",
    instance="martin_grange", 
    channel="ibm_quantum_platform",
    set_as_default=True ,
    overwrite=True
)