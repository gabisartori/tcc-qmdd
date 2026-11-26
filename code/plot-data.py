from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CODE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = CODE_DIR / "results"
OUTPUT_DIR = CODE_DIR / "plots"

# The qubit runner's outer process timeout. Set the layer value once confirmed.
TIME_CEILINGS_SECONDS = {
    "qubits": None,
    "layers": None,
}

SIMULATOR_COLORS = {
    "qmdd": "tab:blue",
    "dense": "tab:orange",
    "sparse": "tab:green",
}

SIMULATOR_LABELS = {
    "qmdd": "QMDD",
    "dense": "Denso",
    "sparse": "Esparso",
}

ALGORITHM_LABELS = {
    "grover": "Grover",
    "falqon": "FALQON",
    "qpe": "Estimação de Fase Quântica",
}


def load_data(filename: str, required_columns: set[str]) -> pd.DataFrame:
    path = RESULTS_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing input CSV: {path}")

    data = pd.read_csv(path)
    missing = required_columns.difference(data.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {', '.join(sorted(missing))}")
    return data


def plot_series(
    ax: plt.Axes,
    data: pd.DataFrame,
    x_column: str,
    time_limit: float | None,
    log_scale: bool = False,
) -> None:
    # Average repeat runs at the same simulator and size.
    grouped = (
        data.groupby(["simulator", x_column], as_index=False)["mean"]
        .mean()
        .sort_values(x_column)
    )

    for simulator, points in grouped.groupby("simulator", sort=True):
        ax.plot(
            points[x_column],
            points["mean"],
            marker="o",
            linewidth=1.8,
            markersize=4,
            color=SIMULATOR_COLORS.get(simulator),
            label=SIMULATOR_LABELS.get(simulator, simulator),
        )

    if log_scale:
        ax.set_yscale("log")
        ax.set_ylabel("Tempo médio de execução (segundos, escala em log)")
    else:
        ax.set_ylabel("Tempo médio de execução (segundos)")
    ax.grid(True, which="both", linestyle=":", alpha=0.5)

    if time_limit is not None:
        ax.axhline(
            time_limit,
            color="black",
            linestyle="--",
            linewidth=1.2,
            label=f"Tempo limite do processo ({time_limit:g} s)",
        )

    ax.legend(title="Simulador")


def main() -> None:
    qubits = load_data(
        "results_qubits.csv",
        {"algorithm", "simulator", "n_qubits", "mean"},
    )
    layers = load_data(
        "results_falqon_layers.csv",
        {"algorithm", "simulator", "n_layers", "mean"},
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for algorithm in ("grover", "falqon", "qpe"):
        subset = qubits.loc[qubits["algorithm"] == algorithm]
        if subset.empty:
            print(f"Não há dados de escalonamento por qubits para {algorithm}; ignorando.")
            continue

        fig, ax = plt.subplots(figsize=(8, 5))
        plot_series(
            ax,
            subset,
            "n_qubits",
            TIME_CEILINGS_SECONDS["qubits"],
            log_scale=True,
        )
        ax.set_xlim(left=14)
        ax.set_title(
            f"{ALGORITHM_LABELS.get(algorithm, algorithm)}: "
            "tempo de execução por número de qubits"
        )
        ax.set_xlabel("Número de qubits")
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / f"{algorithm}_by_qubits.png", dpi=200)
        plt.close(fig)

    falqon_layers = layers.loc[
        (layers["algorithm"] == "falqon") & (layers["simulator"] != "sparse")
    ]
    if falqon_layers.empty:
        print("Não há dados de escalonamento por camadas do FALQON; ignorando.")
    else:
        fig, ax = plt.subplots(figsize=(8, 5))
        plot_series(ax, falqon_layers, "n_layers", TIME_CEILINGS_SECONDS["layers"])
        ax.set_title("FALQON: tempo de execução por número de camadas")
        ax.set_xlabel("Número de camadas")
        fig.tight_layout()
        fig.savefig(OUTPUT_DIR / "falqon_by_layers.png", dpi=200)
        plt.close(fig)

    print(f"Gráficos salvos em {OUTPUT_DIR}")


if __name__ == "__main__":
    main()