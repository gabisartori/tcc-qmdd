from ket import *
from math import pi

def qft(qubits, do_swap: bool = True):
  if len(qubits) == 1:
    H(qubits)
  else:
    *init, last = qubits
    H(last)

    for i, ctrl_qubit in enumerate(reversed(init)):
      with control(ctrl_qubit):
        P(pi / 2 ** (i + 1), last)

    qft(init, do_swap=False)

  if do_swap:
    size = len(qubits)
    for i in range(size // 2):
      SWAP(qubits[i], qubits[size - i - 1])

def estimador_de_fase(oraculo, precisão: int) -> float:
  assert precisão <= 20, "o tempo de computação pode ser muito grande"
  p = Process(simulator="qmdd", num_qubits=precisão + 1)
  ctr = H(p.alloc(precisão))
  tgr = X(p.alloc())
  for i, c in enumerate(ctr):
    ctrl(c, oraculo)(i, tgr)

  adj(qft)(ctr)  # <- chada da transformada de Fourier quântica inversa

  return measure(reversed(ctr)).value / 2**precisão


fase = pi

print(estimador_de_fase(
  oraculo=lambda i, tgr: P(2 * pi * (fase / 10) * 2**i, tgr),
  precisão=18,
) * 10)
