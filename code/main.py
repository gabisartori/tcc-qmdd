from ket import *
import numpy as np

def oracle(target, qubits):
    """Oráculo: inverte a amplitude do estado desejado."""
    with around(
        X,
        qubits.at(i for i, bit in enumerate(f"{target:0{len(qubits)}b}") if bit == "0"),
    ):
        CZ(*qubits)


def diffusion_operator(qubits):
    """Operador de difusão: amplifica as amplitudes dos estados marcados."""
    with around(cat(H, X), qubits):
        ctrl(qubits[:-1], Z)(qubits[-1])  # Controle multi-qubit

from functools import partial


def grover(oracle, qubits):
    """Algoritmo de Grover."""

    n = len(qubits)
    H(qubits)

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
    process = Process(simulator="qmdd")

    # Alocação de n qubits
    qubits = process.alloc(n)

    grover(partial(oracle, target), qubits)

    result = measure(qubits)
    print("Estado encontrado:", result.get())


run_grover(6, 37)