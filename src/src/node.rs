#![allow(dead_code)]
use std::collections::HashMap;
use num::complex::Complex;

fn compare_complex(a: &Complex<f64>, b: &Complex<f64>) -> bool {
  (a - b).norm() < 1e-10
}

const R: usize = 2;

#[derive(Debug, Clone)]
pub struct Node {
  pub id: usize,
  pub variable: usize,
  pub edges: [usize; R*R],
}

#[derive(Debug, Clone)]
pub struct Edge {
  pub id: usize,
  pub target: Option<usize>,
  pub weight: Complex<f64>,
}

impl Edge {
  fn is_terminal(&self) -> bool {
    self.target.is_none()
  }

  fn add(&self, other: &Edge, my_qmdd: &QMDD, other_qmdd: &QMDD, result_qmdd: &mut QMDD) -> usize {
    // If T(e1), swap e0 and e1
    let (e0, e1) = if other.is_terminal() { (self, other) } 
    else { (self, other) };

    // If T(e0) and w(e0) == 0, return e1
    if e0.is_terminal() && compare_complex(&e0.weight, &Complex::new(0.0, 0.0)){
      return result_qmdd.create_edge(e1.target, e1.weight);
    }
    // If T(e0) and T(e1), return new terminal edge with weight w(e0) + w(e1)
    if e0.is_terminal() && e1.is_terminal() {
      return result_qmdd.create_edge(None, e0.weight + e1.weight);
    }

    let mut new_edges = [0; R*R];

    for i in 0..R*R {
      let p = Edge {
        id: 0,
        target: my_qmdd.edges.get(&my_qmdd.nodes.get(&e0.target.unwrap()).unwrap().edges[i]).unwrap().target,
        weight: e0.weight*(my_qmdd.edges.get(&my_qmdd.nodes.get(&e0.target.unwrap()).unwrap().edges[i]).unwrap().weight),
      };
      let q = Edge {
        id: 0,
        target: other_qmdd.edges.get(&other_qmdd.nodes.get(&e1.target.unwrap()).unwrap().edges[i]).unwrap().target,
        weight: e1.weight*(other_qmdd.edges.get(&other_qmdd.nodes.get(&e1.target.unwrap()).unwrap().edges[i]).unwrap().weight),
      };
      let r = p.add(&q, my_qmdd, other_qmdd, result_qmdd);
      new_edges[i] = r;
    }
    let new_node = result_qmdd.create_node(
      my_qmdd.nodes.get(&e0.target.unwrap()).unwrap().variable,
      new_edges
    );
    let new_edge = result_qmdd.create_edge(new_node, Complex::new(1.0, 0.0));
    new_edge
  }

  fn multiply(&self, other: &Edge, my_qmdd: &QMDD, other_qmdd: &QMDD, result_qmdd: &mut QMDD) -> usize {
    // If T(e1), swap e0 and e1
    let (e0, e1) = if other.is_terminal() { (self, other) } 
    else { (self, other) };

    if e0.is_terminal() {
      if compare_complex(&e0.weight, &Complex::new(0.0, 0.0)){ return result_qmdd.create_edge(e0.target, e0.weight); }
      if compare_complex(&e0.weight, &Complex::new(0.0, 0.0)){ return result_qmdd.create_edge(e0.target, e0.weight); }
      return result_qmdd.create_edge(None, e0.weight * e1.weight);
    }

    let mut new_edges = [0; R*R];
    for i in 0..R {
      for j in 0..R {
        for k in 0..R {
          let p = Edge {
            id: 0,
            target: my_qmdd.edges.get(&my_qmdd.nodes.get(&e0.target.unwrap()).unwrap().edges[i*R + k]).unwrap().target,
            weight: e0.weight*(my_qmdd.edges.get(&my_qmdd.nodes.get(&e0.target.unwrap()).unwrap().edges[i*R + k]).unwrap().weight),
          };
          let q = Edge {
            id: 0,
            target: other_qmdd.edges.get(&other_qmdd.nodes.get(&e1.target.unwrap()).unwrap().edges[k*R + j]).unwrap().target,
            weight: e1.weight*(other_qmdd.edges.get(&other_qmdd.nodes.get(&e1.target.unwrap()).unwrap().edges[k*R + j]).unwrap().weight),
          };
          let r = p.multiply(&q, my_qmdd, other_qmdd, result_qmdd);
          if new_edges[i*R + j] == 0 {
            new_edges[i*R + j] = r;
          } else {
            let temp_edge = result_qmdd.edges.get(&new_edges[i*R + j]).unwrap().clone();
            let summed_edge = temp_edge.add(&Edge { id: 0, target: result_qmdd.edges.get(&r).unwrap().target, weight: result_qmdd.edges.get(&r).unwrap().weight }, my_qmdd, other_qmdd, result_qmdd);
            new_edges[i*R + j] = summed_edge;
          }
        }
      }
    }
    let new_node = result_qmdd.create_node(
      my_qmdd.nodes.get(&e0.target.unwrap()).unwrap().variable,
      new_edges
    );
    let new_edge = result_qmdd.create_edge(new_node, Complex::new(1.0, 0.0));
    new_edge
  }

  fn kronecker(&self, other: &Edge, my_qmdd: &QMDD, other_qmdd: &QMDD, result_qmdd: &mut QMDD) -> usize {
    if self.is_terminal() {
      if compare_complex(&self.weight, &Complex::new(0.0, 0.0)) {
        return result_qmdd.create_edge(self.target, self.weight);
      } else if compare_complex(&self.weight, &Complex::new(1.0, 0.0)) {
        return result_qmdd.create_edge(other.target, other.weight);
      } else {
        return result_qmdd.create_edge(other.target, self.weight * other.weight);
      }
    }
  
    let mut new_edges = [0; R*R];
    for i in 0..R*R {
      let p = my_qmdd.edges.get(&my_qmdd.nodes.get(&self.target.unwrap()).unwrap().edges[i]).unwrap();
      let r = p.kronecker(other, my_qmdd, other_qmdd, result_qmdd);
      new_edges[i] = r;
    }
    let new_node = result_qmdd.create_node(
      my_qmdd.nodes.get(&self.target.unwrap()).unwrap().variable + other_qmdd.nodes.get(&other.target.unwrap()).unwrap().variable,
      new_edges
    );
    let new_edge = result_qmdd.create_edge(new_node, Complex::new(1.0, 0.0));
    new_edge
  }
}

#[derive(Clone, Debug)]
pub struct QMDD {
  root: usize,
  nodes: HashMap<usize, Node>,
  edges: HashMap<usize, Edge>,
}

impl QMDD {
  pub fn new() -> Self {
    QMDD {
      root: 0,
      nodes: HashMap::new(),
      edges: HashMap::new(),
    }
  }

  // TODO: Give this a proper name, also implement a n dimensional identity creation instead of hardcoding a 2d one
  pub fn eye() -> Self {
    let mut qmdd = QMDD::new();
    qmdd.insert_node(Node{ id: 0, variable: 0, edges: [1, 2, 1, 2] });
    qmdd.insert_edge(Edge{ id: 0, target: Some(0), weight: Complex::new(1.0, 0.0) });
    qmdd.insert_edge(Edge{ id: 1, target: None, weight: Complex::new(1.0, 0.0) });
    qmdd.insert_edge(Edge{ id: 2, target: None, weight: Complex::new(0.0, 0.0) });
    qmdd
  }

  pub fn hadamard() -> Self {
    let mut qmdd = QMDD::new();
    qmdd.insert_node(Node{ id: 0, variable: 0, edges: [1, 1, 1, 2] });
    qmdd.insert_edge(Edge{ id: 0, target: Some(0), weight: Complex::new(1.0/(2.0f64).sqrt(), 0.0) });
    qmdd.insert_edge(Edge{ id: 1, target: None, weight: Complex::new(1.0, 0.0) });
    qmdd.insert_edge(Edge{ id: 2, target: None, weight: Complex::new(-1.0, 0.0) });
    qmdd 
  }

  pub fn antieye() -> Self {
    let mut qmdd = QMDD::new();
    qmdd.insert_node(Node{ id: 0, variable: 0, edges: [2,1,2,1] });
    qmdd.insert_edge(Edge{ id: 0, target: Some(0), weight: Complex::new(1.0, 0.0) });
    qmdd.insert_edge(Edge{ id: 1, target: None, weight: Complex::new(1.0, 0.0) });
    qmdd.insert_edge(Edge{ id: 2, target: None, weight: Complex::new(0.0, 0.0) });
    qmdd 
  }

  // pub fn ket_0(num_qubits: usize) -> Self {
  //   let mut nodes = HashMap::new();
  //   let mut edges = HashMap::new();

  //   for i in (0..num_qubits).rev() {
  //     let node_id = num_qubits - i - 1;
  //     let edge_zero = if i == num_qubits - 1 { edges.len() } else { node_id + 1 };

  //     let edge_one = edges.len() + 1;

  //     nodes.insert(node_id, Node {
  //       id: node_id,
  //       variable: i,
  //       edges: [edge_zero, edge_one, edge_zero, edge_one],
  //     });

  //     edges.insert(edge_zero, Edge {
  //       id: edge_zero,
  //       target: Some(node_id + 1).filter(|&x| x < num_qubits),
  //       weight: Complex::new(1.0, 0.0),
  //     });

  //     edges.insert(edge_one, Edge {
  //       id: edge_one,
  //       target: None,
  //       weight: Complex::new(0.0, 0.0),
  //     });
  //   }

  //   QMDD { root: 0, nodes, edges }
  // }

  pub fn insert_node(&mut self, node: Node) { self.nodes.insert(node.id, node); }

  pub fn insert_edge(&mut self, edge: Edge) { self.edges.insert(edge.id, edge); }

  pub fn create_edge(&mut self, target: Option<usize>, weight: Complex<f64>) -> usize {
    let mut new_id = 0;
    for (id, edge) in &self.edges {
      if edge.target == target && (edge.weight - weight).norm() < 1e-10 {
        return *id;
      }
      new_id = new_id.max(*id);
    }
    let new_edge = Edge { id: new_id + 1, target, weight };
    self.insert_edge(new_edge);
    new_id + 1
  }

  pub fn create_node(&mut self, variable: usize, edges: [usize; R*R]) -> Option<usize> {
    // Skip node creation if all the edges are the same
    
    // Normalize edges
    // Every edge that points to the created node must have its weight divided by the weight of the first edge
    let mut new_edges = [0; R*R];
    let edge_0_weight = self.get_edge(edges[0]).weight;
    for i in 0..R*R {
      let edge = self.get_edge(edges[i]);
      new_edges[i] = self.create_edge(edge.target, edge.weight/edge_0_weight);
    }
    let edges = new_edges;
    for i in 1..R*R {
      let (prev, curr) = (self.get_edge(edges[i-1]), self.get_edge(edges[i]));
      // Break when a different edge is found
      if prev.target != curr.target || prev.weight != curr.weight {
        break;
      }
      // If loop reaches the last edge, then all edges were the same so return node can be ignored
      if i == R*R - 1 { return self.get_edge(edges[0]).target; }
    }

    let mut new_id = 0;
    for (id, node) in &self.nodes {
      if node.variable == variable && node.edges == edges {
        return Some(*id);
      }
      new_id = new_id.max(*id);
    }
    let new_node = Node { id: new_id + 1, variable, edges };
    self.insert_node(new_node);
    Some(new_id + 1)
  }

  pub fn get_root(&self) -> &Edge {
    self.edges.get(&self.root).unwrap()
  }

  fn get_edge(&self, edge_id: usize) -> &Edge {
    self.edges.get(&edge_id).unwrap()
  }

  pub fn traverse(&self) -> Vec<Complex<f64>> {
    let mut results = Vec::new();
    if let Some(start_edge) = self.edges.get(&self.root) {
      self.traverse_inner(start_edge, start_edge.weight, &mut results);
    }
    results
  }

  pub fn add(&self, other: &QMDD) -> QMDD {
    let mut result_qmdd = QMDD::new();
    let root = self.get_root().add(other.get_root(), self, other, &mut result_qmdd);
    result_qmdd.root = root;
    result_qmdd
  }

  // TODO: Some edges are being inserted in the resulting QMDD that are not used
  pub fn multiply(&self, other: &QMDD) -> QMDD {
    let mut result_qmdd = QMDD::new();
    let root = self.get_root().multiply(other.get_root(), self, other, &mut result_qmdd);
    result_qmdd.root = root;
    result_qmdd
  }

  pub fn kronecker(&self, other: &QMDD) -> QMDD {
    let mut result_qmdd = QMDD::new();
    let root = self.get_root().kronecker(other.get_root(), self, other, &mut result_qmdd);
    result_qmdd.root = root;
    result_qmdd
  }

  fn traverse_inner(&self, edge: &Edge, value: Complex<f64>, results: &mut Vec<Complex<f64>>) {
    if edge.is_terminal() {
      results.push(value);
      return;
    }
    if let Some(target_id) = edge.target {
      if let Some(node) = self.nodes.get(&target_id) {
        for i in 0..R {
          let edge_id = node.edges[i];
          if let Some(next_edge) = self.edges.get(&edge_id) {
            self.traverse_inner(next_edge, value * next_edge.weight, results);
          }
        }
      }
    }
  }
}

// impl std::fmt::Debug for QMDD {
//   fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
//     fn trave
//     writeln!(f, "QMDD {{")?;
//     writeln!(f, "  root: {}", self.root)?;
//     writeln!(f, "  nodes: [")?;
//     for node in self.nodes.values() {
//       writeln!(f, "    {:?},", node)?;
//     }
//     writeln!(f, "  ]")?;
//     writeln!(f, "  edges: [")?;
//     for edge in self.edges.values() {
//       writeln!(f, "    {:?},", edge)?;
//     }
//     writeln!(f, "  ]")?;
//     writeln!(f, "}}")
//   }
// }
