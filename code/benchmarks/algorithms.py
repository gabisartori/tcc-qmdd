import argparse

from falqon import run_falqon

args = argparse.ArgumentParser(description="Benchmark de Simuladores Quânticos")

args.add_argument("simulator", type=str, default="dense", help="Simulador utilizado")
args.add_argument("qubits", type=int, default=10, help="Número de qubits")

args = args.parse_args()

algorithm = "falqon"

match algorithm:
  case "falqon":
    run_falqon(args.qubits, args.simulator)
  case _:
    raise ValueError(f"Algoritmo desconhecido: {algorithm}")
