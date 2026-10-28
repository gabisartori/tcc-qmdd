import ket as k

process = k.Process()
a, b = process.alloc(2)
k.CNOT(k.H(a), b)
print(k.dump(a+b).show())
