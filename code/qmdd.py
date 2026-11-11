from dataclasses import dataclass

COMPLEX_ZERO = 0.0 + 0.0j
COMPLEX_ONE = 1.0 + 0.0j
COMPLEX_INVERSE_SQRT_2 = 1.0 / (2.0 ** 0.5) + 0.0j
COMPLEX_NEG_INVERSE_SQRT_2 = -1.0 / (2.0 ** 0.5) + 0.0j

I_MATRIX = [
  COMPLEX_ONE,
  COMPLEX_ZERO,
  COMPLEX_ZERO,
  COMPLEX_ONE
]

IF_FALSE_MATRIX = [
  COMPLEX_ONE,
  COMPLEX_ZERO,
  COMPLEX_ZERO,
  COMPLEX_ZERO
]

IF_TRUE_MATRIX = [
  COMPLEX_ZERO,
  COMPLEX_ZERO,
  COMPLEX_ZERO,
  COMPLEX_ONE
]

PAULI_X_MATRIX = [
  COMPLEX_ZERO,
  COMPLEX_ONE,
  COMPLEX_ONE,
  COMPLEX_ZERO
]

PAULI_Y_MATRIX = [
  COMPLEX_ZERO,
  -1.0j,
  1.0j,
  COMPLEX_ZERO
]

PAULI_Z_MATRIX = [
  COMPLEX_ONE,
  COMPLEX_ZERO,
  COMPLEX_ZERO,
  -COMPLEX_ONE
]

HADAMARD_MATRIX = [
  COMPLEX_INVERSE_SQRT_2,
  COMPLEX_INVERSE_SQRT_2,
  COMPLEX_INVERSE_SQRT_2,
  COMPLEX_NEG_INVERSE_SQRT_2
]

M0_MATRIX = [
  COMPLEX_ONE,
  COMPLEX_ZERO,
  COMPLEX_ZERO,
  COMPLEX_ZERO
]

M1_MATRIX = [
  COMPLEX_ZERO,
  COMPLEX_ZERO,
  COMPLEX_ZERO,
  COMPLEX_ONE
]

@dataclass
class Node:
  var: int
  edges: list['Edge']

  def __hash__(self):
    return hash(id(self))

@dataclass
class Edge:
  weight: complex
  node: Node

@dataclass
class Gate:
  controls: list[int]
  target: int
  matrix: list[complex]


class Qmdd:
  def __init__(self, num_vars: int):
    self.num_vars = num_vars
    self.terminal_node = Node(-1, [])
    self.root = Edge(COMPLEX_ONE, self.terminal_node)

    for var in reversed(range(num_vars)):
      i_edge = self.local_operator_edge(var, I_MATRIX)
      self.root = self.kro_edge(i_edge, self.root)

  def make_node(
      self,
      var: int,
      edges: list[Edge]
  ) -> Edge:
    if all(edge == edges[0] for edge in edges):
      return edges[0]

    pivot_idx = 0
    for i, edge in enumerate(edges):
      if edge.weight != COMPLEX_ZERO:
        pivot_idx = i
        break

    pivot = edges[pivot_idx].weight
    new_edges = [
      Edge(edge.weight / pivot, edge.node) for edge in edges
    ]
    return Edge(pivot, Node(var, new_edges))

  def local_operator_edge(self, var: int, matrix: list[complex]) -> Edge:
    return Edge(COMPLEX_ONE, Node(
      var,
      [Edge(child, self.terminal_node) for child in matrix]
    ))

  def terminal(self, edge: Edge) -> bool:
    return edge.node.var == -1

  def zero_edge(self) -> Edge:
    return Edge(COMPLEX_ZERO, self.terminal_node)

  def add_edge(self, e0: Edge, e1: Edge) -> Edge:
    if self.terminal(e1):
      e0, e1 = e1, e0

    if self.terminal(e0):
      if e0.weight == COMPLEX_ZERO:
        return e1
      if self.terminal(e1):
        return Edge(e0.weight + e1.weight, self.terminal_node)

    z = [self.add_edge(
      Edge(
        e0.weight * e0.node.edges[i].weight,
        e0.node.edges[i].node
      ),
      Edge(
        e1.weight * e1.node.edges[i].weight,
        e1.node.edges[i].node
      )
    ) for i in range(4)]

    return self.make_node(e0.node.var, z)

  def mul_edge(self, e0: Edge, e1: Edge) -> Edge:
    if self.terminal(e1):
      e0, e1 = e1, e0

    if self.terminal(e0):
      if e0.weight == COMPLEX_ZERO:
        return e0
      if e0.weight == COMPLEX_ONE:
        return e1
      return Edge(e0.weight * e1.weight, e1.node)

    z = [self.zero_edge() for _ in range(4)]
    for i in range(0, 4, 2):
      for j in range(2):
        zij = self.zero_edge()
        for k in range(2):
          ei0 = e0.node.edges[i + k]
          p = Edge(
            e0.weight * ei0.weight,
            ei0.node
          )
          ei1 = e1.node.edges[2 * k + j]
          q = Edge(
            e1.weight * ei1.weight,
            ei1.node
          )
          q0q1 = self.mul_edge(p, q)
          zij = self.add_edge(zij, q0q1)
        z[i + j] = zij

    return self.make_node(e0.node.var, z)

  def kro_edge(self, e0: Edge, e1: Edge) -> Edge:
    if self.terminal(e0):
      if e0.weight == COMPLEX_ZERO:
        return e0
      if e0.weight == COMPLEX_ONE:
        return e1
      return Edge(e0.weight * e1.weight, e1.node)

    z = [self.zero_edge() for _ in range(4)]
    for i in range(4):
      z[i] = self.kro_edge(
        e0.node.edges[i],
        e1
      )
    e = self.make_node(e0.node.var, z)
    e.weight *= e0.weight
    return e

  def apply_gate(self, gate: Gate) -> None:
    matrices = [
      self.local_operator_edge(qubit, gate.matrix if qubit == gate.target else I_MATRIX)
      for qubit in reversed(range(self.num_vars))
    ]
    e0 = matrices[0]
    for e in matrices[1:]:
      e0 = self.kro_edge(e, e0)
    self.root = self.mul_edge(e0, self.root)

  def reconstruct_state(self) -> list[complex]:
    dim = 2 ** self.num_vars
    state = [COMPLEX_ZERO for _ in range(dim)]
    for i in range(dim):
      edge = self.root
      value = edge.weight
      qubit_idx = self.num_vars - 1
      while True:
        if self.terminal(edge): break
        bit = (i >> qubit_idx) & 1
        edge_idx = 0 if bit == 0 else 2
        value *= edge.node.edges[edge_idx].weight
        edge = edge.node.edges[edge_idx]
        qubit_idx -= 1
      state[i] = value
    return state

  def traverse(self) -> int:
    visited = set()
    stack = [self.root.node]
    count = 0
    while stack:
      node = stack.pop()
      if node in visited:
        continue
      visited.add(node)
      count += 1
      for edge in node.edges:
        if not self.terminal(edge):
          stack.append(edge.node)
    return count
size = 10

sim = Qmdd(size)
for i in range(size):
  print(f"Applying Hadamard gate to qubit {i}")
  sim.apply_gate(Gate([], i, HADAMARD_MATRIX))
  print(f"Number of nodes after applying gate: {sim.traverse()}")

print(sim.reconstruct_state())