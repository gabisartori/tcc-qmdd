from ket import *
from math import pi
import argparse

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

def qpe(p, oracle, qubits: int) -> float:
  ctr = H(p.alloc(qubits-1))
  tgr = X(p.alloc())
  for i, c in enumerate(ctr):
    ctrl(c, oracle)(i, tgr)

  adj(qft)(ctr)  # <- chada da transformada de Fourier quântica inversa

  return measure(reversed(ctr)).value / 2**qubits

def oracle(i, tgr):
  phase = 2*pi/10 # The phase to be estimated doesn't affect the number of iterations, so we can use any value here.
  P(2 * pi * phase * 2**i, tgr)

def run_qpe(n: int, simulator: str):
  p = Process(simulator=simulator, num_qubits=n)
  return qpe(p, oracle, n)*10


args = argparse.ArgumentParser(description="Algoritmo de Estimação de Fase Quântica")
args.add_argument("simulator", type=str, default="dense", help="Simulador utilizado")
args.add_argument("n", type=int, default=10, help="Número de qubits")
args = args.parse_args()

assert args.n >= 2, "This algorithm needs at least 2 qubits, one for the target and one for the precision."
print(run_qpe(args.n, args.simulator))