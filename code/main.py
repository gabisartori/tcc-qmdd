import ket as k

p = k.Process(simulator="qmdd")
qubits = p.alloc(3)

k.X(qubits[0])
k.H(qubits[2])

k.ctrl(qubits[0]+qubits[2], k.X)(qubits[1])
print(k.dump(qubits).show())
