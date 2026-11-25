import ket as k
import numpy as np
from functools import partial
import argparse

def oracle(target, qubits):
    for i, qubit in enumerate(qubits):
        if ((target >> i) & 1) == 0:
            k.X(qubit)

    k.H(qubits[-1])
    k.ctrl(qubits[:-1], k.Z)(qubits[-1])
    k.H(qubits[-1])

    for i, qubit in enumerate(qubits):
        if ((target >> i) & 1) == 0:
            k.X(qubit)


def diffusion_operator(qubits):
    k.H(qubits)
    k.X(qubits)
    k.H(qubits[-1])
    k.ctrl(qubits[:-1], k.Z)(qubits[-1])
    k.H(qubits[-1])
    k.X(qubits)
    k.H(qubits)


def grover(oracle, qubits):
  """Algoritmo de Grover."""

  n = len(qubits)
  k.H(qubits)

  # Número ideal de iterações: sqrt(2^n)
  iterations = int((np.pi / 4) * np.sqrt(2**n))

  # Iterações do algoritmo de Grover
  for _ in range(iterations):
    oracle(qubits)
    diffusion_operator(qubits)

def run_grover(n: int, simulator):
  """Executa o algoritmo de Grover."""
  process = k.Process(simulator=simulator, num_qubits=n)

  qubits = process.alloc(n)
  # The searched value does not affect the number of iterations, so we can use any value here.
  grover(partial(oracle, 1), qubits)
  print(k.measure(qubits).get())

args = argparse.ArgumentParser(description="Algoritmo de Grover")
args.add_argument("simulator", type=str, default="dense", help="Simulador utilizado")
args.add_argument("n", type=int, default=10, help="Número de qubits")
args = args.parse_args()

run_grover(args.n, args.simulator)

