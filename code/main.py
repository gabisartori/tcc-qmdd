import ket as k

p = k.Process(simulator="qmdd")
qubits = p.alloc(5)


k.H(qubits)

print(k.dump(qubits).show())
print("\nMeasure: ", k.measure(qubits[0]).get(), '\n')
print(k.dump(qubits).show())
