#![allow(unused_imports)]
use std::collections::HashMap;

use num::complex::Complex;


mod node;
use node::*;

fn main() {
  let qmdd1 = QMDD::hadamard();
  let qmdd2 = QMDD::hadamard();
  println!("{:?}", qmdd1.kronecker(&qmdd2));
  println!("{:?}", qmdd1.traverse());
}
