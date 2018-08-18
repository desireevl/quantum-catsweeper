from qiskit import QuantumProgram
from enum import Enum
import math

import qconfig
import random
import quantumrandom as qr

real_device = False
shots = 1024

device = 'local_qasm_simulator'
if real_device:
    device = 'ibmqx4'

num_clicks = 1

Q_program = QuantumProgram()
Q_program.set_api(qconfig.APItoken, qconfig.config["url"])
q = Q_program.create_quantum_register("q", 5)
c = Q_program.create_classical_register("c", 5)
gridScript = Q_program.create_circuit("gridScript", [q], [c])


gridScript.u3(1/3 * math.pi, 0.0, 0.0, q[2])
gridScript.u3(1/3 * math.pi, 0.0, 0.0, q[2])
gridScript.u3(1/3 * math.pi, 0.0, 0.0, q[2])

gridScript.measure(q[2], c[2])
results = Q_program.execute(["gridScript"], backend=device, shots=shots, wait=5, timeout=1800)
re = results.get_counts("gridScript")
print(re)