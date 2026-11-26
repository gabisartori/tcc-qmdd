from pathlib import Path
import re
import sys
import warnings

import pandas as pd


ROOT = Path(__file__).resolve().parent / "results"
TIMESTAMP_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})-(?P<details>.+)$"
)
QUBITS_RE = re.compile(
    r"^(?P<simulator>[^-]+)-(?P<algorithm>.+)-(?P<n_qubits>\d+)$"
)


def read_result(path: Path, experiment: str) -> dict | None:
    match = TIMESTAMP_RE.fullmatch(path.stem)
    if not match:
        raise ValueError(f"Unrecognized filename format: {path}")

    details = match.group("details")
    if experiment == "layers":
        try:
            simulator, n_qubits, n_layers = details.rsplit("-", 2)
            metadata = {
                "experiment": "layers",
                "timestamp": match.group("timestamp"),
                "simulator": simulator,
                "algorithm": "falqon",
                "n_qubits": int(n_qubits),
                "n_layers": int(n_layers),
            }
        except ValueError as exc:
            raise ValueError(f"Unrecognized layer filename format: {path}") from exc
    else:
        details_match = QUBITS_RE.fullmatch(details)
        if not details_match:
            raise ValueError(f"Unrecognized qubit filename format: {path}")
        metadata = {
            "experiment": "qubits",
            "timestamp": match.group("timestamp"),
            "simulator": details_match.group("simulator"),
            "algorithm": details_match.group("algorithm"),
            "n_qubits": int(details_match.group("n_qubits")),
            "n_layers": pd.NA,
        }

    try:
        data = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        warnings.warn(f"Skipping empty CSV: {path}", stacklevel=2)
        return None

    if data.empty:
        warnings.warn(f"Skipping CSV with no data rows: {path}", stacklevel=2)
        return None

    data["source_file"] = str(path.relative_to(ROOT))
    for key, value in metadata.items():
        data[key] = value
    return data


def collect(directory: Path, experiment: str) -> pd.DataFrame:
    frames = []
    for path in sorted(directory.rglob("*.csv")):
        frame = read_result(path, experiment)
        if frame is not None:
            frames.append(frame)

    if not frames:
        raise RuntimeError(f"No readable CSV data found under {directory}")

    result = pd.concat(frames, ignore_index=True, sort=False)
    return result.sort_values(
        ["simulator", "algorithm", "n_qubits", "n_layers", "timestamp"],
        na_position="first",
        kind="stable",
    )


def main() -> None:
    qubits = collect(ROOT / "qubits", "qubits")
    layers = collect(ROOT / "layers", "layers")

    qubits.to_csv(ROOT / "results_qubits.csv", index=False)
    layers.to_csv(ROOT / "results_falqon_layers.csv", index=False)

    print(f"Wrote {len(qubits)} qubit-scaling rows and {len(layers)} layer-scaling rows.")


if __name__ == "__main__":
    main()