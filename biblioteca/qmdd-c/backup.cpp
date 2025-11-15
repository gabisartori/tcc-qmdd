void write_dot(
  const char* title,
  const program_spec& spec, const qmdd& dd,
  const qmdd::edge& root,
  const char* fn
) {
  static const int p = qmdd::p;

  FILE* f = fopen(fn, "w");

  if (!f) {
    throw std::runtime_error(std::string("failed to open ") + fn);
  }

  fprintf(f, "digraph {\n");

  fprintf(f, "  labelloc=\"t\";\n");
  fprintf(f, "  label=\"%s\";\n", title);
  fprintf(f, "  splines=line;\n");

  std::vector<qmdd::node_handle> nodes2add = { root.v };

  qmdd::node_handle true_node = dd.get_true();

  struct node_hasher {
    auto operator()(qmdd::node_handle n) const {
      return n.value;
    }
  };

  std::unordered_set<qmdd::node_handle, node_hasher> added;
  added.insert(true_node);

  std::unordered_set<qmdd::node_handle, node_hasher> declared;
  
  fprintf(f, "  root [shape=point,width=0.001,height=0.001];\n");
  fprintf(f, "  root -> n%u [label=\"%s\"];\n", root.v.value, dd.to_string(root.w).c_str());

  if (root.v == true_node) {
    fprintf(f, "  n%u [label=\"1\",shape=box];\n", true_node.value);
  }
  else {
    fprintf(f, "  n%u [label=\"%s\",shape=circle];\n", root.v.value, spec.variable_names[dd.get_var(root.v)].c_str());
  }

  declared.insert(root.v);

  while (!nodes2add.empty()) {
    qmdd::node_handle n = nodes2add.back();
    nodes2add.pop_back();

    if (added.find(n) != end(added))
      continue;

    qmdd::node_handle children[p * p];
    dd.get_children(n, children);

    qmdd::weight_handle weights[p * p];
    dd.get_weights(n, weights);

    for (int child_idx = 0; child_idx < p * p; child_idx++) {
      qmdd::node_handle child = children[child_idx];

      if (declared.insert(child).second) {
        if (child == true_node) {
          fprintf(f, "  n%u [label=\"1\",shape=box];\n", child.value);
        }
        else {
          fprintf(f, "  n%u [label=\"%s\",shape=circle];\n", child.value, spec.variable_names[dd.get_var(child)].c_str());
        }
      }

      if (added.find(child) == end(added))
        nodes2add.push_back(child);
    }

    // "invisible" row of nodes for the child weights, then point those invisible nodes to the real nodes.
    fprintf(f, "  subgraph c%u {\n", n.value); {
      fprintf(f, "  rank=same;\n");
      fprintf(f, "  edge[style=invisible,dir=none];\n");

      for (int i = 0; i < p * p; i++) {
        const char* color = i % 2 == 0 ? "red" : "black";

        if (weights[i] == qmdd::weight_0_handle) {
          fprintf(f, "  c%u_%d[shape=point,color=%s];\n", n.value, i, color);
        }
        else {
          fprintf(f, "  c%u_%d[shape=point,width=0.01,height=0.01,color=%s];\n", n.value, i, color);
        }
      }

      // used for rank order...
      fprintf(f, "  c%u_%d[shape=point,width=0,height=0,style=invis];\n", n.value, p*p);

      for (int i = 0; i <= p * p; i++) {
        if (i == 0)
          fprintf(f, "  ");
        else
          fprintf(f, " -> ");

        if (i == p*p / 2) {
          // putting the invisible node here make the children more centered
          fprintf(f, "c%u_%d", n.value, p*p);
        }
        else if (i > p*p / 2) {
          fprintf(f, "c%u_%d", n.value, i - 1);
        }
        else {
          fprintf(f, "c%u_%d", n.value, i);
        }
      }

      fprintf(f, ";\n");
    }
    fprintf(f, "  }\n");

    for (int i = 0; i < p * p; i++) {
      const char* color = i % 2 == 0 ? "red" : "black";
      fprintf(f, "  n%u -> c%u_%d [label=\"%s\", arrowhead=none,color=%s,fontcolor=%s];\n", n.value, n.value, i, dd.to_string(weights[i]).c_str(), color, color);
    }

    for (int i = 0; i < p * p; i++) {
      if (weights[i] == qmdd::weight_0_handle) continue;

      const char* color = i % 2 == 0 ? "red" : "black";
      fprintf(f, "  c%u_%d -> n%u [constraint=false,color=%s];\n", n.value, i, children[i].value, color);
      fprintf(f, "  c%u_%d -> n%u [style=invis];\n", n.value, p*p, children[i].value);
    }

    added.insert(n);
  }

  fprintf(f, "}\n");

  fclose(f);
}



// main
// Export described circuit to dot file
std::string outfilename = infilename + ".dot";
write_dot(infilename.c_str(), spec, dd, root, outfilename.c_str());
