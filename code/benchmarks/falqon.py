from ket import *

import argparse
from math import ceil, sqrt

def cost_h(edges, qubits):
  with obs():
    return -1 / 2 * sum(1 - Z(qubits[a]) * Z(qubits[b]) for a, b in edges)

def mixer_h(qubits):
  with obs():
    return sum(X(q) for q in qubits)

def beta_h(arestas, qubits):
  h = 1j * commutator(mixer_h(qubits), cost_h(arestas, qubits))
  return -h

def falqon_layer(edges, delta_t, beta, qubits):
  evolve(cost_h(edges, qubits) * delta_t)
  evolve(mixer_h(qubits) * delta_t * beta)

def run_falqon(num_qubits, simulator="dense"):
  # Initial values
  delta_t = 0.1
  num_layers = 10

  betas = [0.0]
  cost = []

  num_nodes = ceil(sqrt(num_qubits))

  edges = [
    (i, j) for i in range(num_nodes) for j in range(i + 1, num_nodes)
  ][:num_qubits]

  process = Process(simulator=simulator, num_qubits=num_qubits-1)
  qubits = process.alloc(num_qubits-1)

  # Initialize circuit at |+>^n
  H(qubits)

  # Run optimization layers
  for _ in range(num_layers):
    falqon_layer(edges, delta_t, betas[-1], qubits)

    cost.append(exp_value(cost_h(edges, qubits)).get())
    betas.append(exp_value(beta_h(edges, qubits)).get())

args = argparse.ArgumentParser(description="Algoritmo Falqon")
args.add_argument("simulator", type=str, default="dense", help="Simulador utilizado")
args.add_argument("n", type=int, default=10, help="Número de qubits")
args = args.parse_args()

assert args.n >= 3, "Número de qubits deve ser maior ou igual a 3"

run_falqon(args.n, args.simulator)
