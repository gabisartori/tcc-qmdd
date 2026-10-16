import ket as k

p = k.Process(simulator="qmdd")
a, b = p.alloc(2)
k.CNOT(k.H(a), b)
print(k.dump(a+b).show())
