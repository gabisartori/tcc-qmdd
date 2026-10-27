import ket as k
import numpy as np

def oracle(target, qubits):
  """Oráculo: inverte a amplitude do estado desejado."""
  with k.around(
    k.X,
    qubits.at(i for i, bit in enumerate(f"{target:0{len(qubits)}b}") if bit == "0"),
  ):
    k.CZ(*qubits)


def diffusion_operator(qubits):
  """Operador de difusão: amplifica as amplitudes dos estados marcados."""
  with k.around(k.cat(k.H, k.X), qubits):
    k.ctrl(qubits[:-1], k.Z)(qubits[-1])  # Controle multi-qubit

from functools import partial


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

from functools import partial


def run_grover(n, target):
  """Executa o algoritmo de Grover."""
  # Inicialização do processo
  process = k.Process(simulator="dense")

  # Alocação de n qubits
  qubits = process.alloc(n)
  grover(partial(oracle, target), qubits)
  print(k.measure(qubits).get())

run_grover(18, 150)
