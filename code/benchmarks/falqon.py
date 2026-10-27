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

edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)]
num_nodes = len(edges) - 1

delta_t = 0.1
qulib.draw(falqon_layer, num_nodes, (edges, delta_t, 2.4))
num_layers = 10

betas = [0.0]
cost = []

process = Process()
qubits = process.alloc(num_nodes)
H(qubits)

for _ in range(num_layers):
  falqon_layer(edges, delta_t, betas[-1], qubits)

  cost.append(exp_value(cost_h(edges, qubits)).get())
  betas.append(exp_value(beta_h(edges, qubits)).get())

print(cost)
print(betas)