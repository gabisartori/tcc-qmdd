from ket import *

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

def run_falqon(num_edges, simulator="dense"):
  edges = [
    (i, j) for i in range(num_edges) for j in range(i + 1, num_edges)
  ]
  num_nodes = len(edges) - 1

  delta_t = 0.1
  num_layers = 10

  betas = [0.0]
  cost = []

  process = Process(simulator=simulator, num_qubits=num_nodes)
  qubits = process.alloc(num_nodes)
  H(qubits)

  for _ in range(num_layers):
    falqon_layer(edges, delta_t, betas[-1], qubits)

    cost.append(exp_value(cost_h(edges, qubits)).get())
    betas.append(exp_value(beta_h(edges, qubits)).get())
