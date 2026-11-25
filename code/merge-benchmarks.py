import os
import re

import pandas as pd


root = "results"
rows = []

for directory, _, files in os.walk(root):
    for filename in sorted(files):
        if not filename.endswith(".csv"):
            continue

        path = os.path.join(directory, filename)
        print(filename)

        stem = filename[:-4]
        match = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})-(.+)$", stem)
        if match is None:
            print(f"Skipping unrecognized filename: {filename}")
            continue

        date, suffix = match.groups()
        parts = suffix.rsplit("-", 2)
        if len(parts) != 3:
            print(f"Skipping unrecognized filename: {filename}")
            continue

        try:
            df = pd.read_csv(path)
        except pd.errors.EmptyDataError:
            continue
        if df.empty:
            continue

        benchmark = df.iloc[0]
        command = str(benchmark["command"])
        command_parts = command.split()

        # FALQON: <simulator>-<n_qubits>-<n_layers>
        # General benchmarks: <simulator>-<algorithm>-<n_qubits>
        if len(command_parts) >= 5:
            simulator = command_parts[2]
            algorithm = os.path.splitext(os.path.basename(command_parts[1]))[0]
            n_qubits = int(command_parts[3])
            n_layers = int(command_parts[4]) if algorithm == "falqon" else 1
        elif len(command_parts) >= 4:
            simulator = command_parts[2]
            algorithm = os.path.splitext(os.path.basename(command_parts[1]))[0]
            n_qubits = int(command_parts[3])
            n_layers = 1
        else:
            simulator, n_qubits, n_layers = parts
            n_qubits = int(n_qubits)
            n_layers = int(n_layers)
            algorithm = os.path.basename(directory)

        rows.append({
            "date": date,
            "simulator": simulator,
            "algorithm": algorithm,
            "n_qubits": n_qubits,
            "n_layers": n_layers,
            "command": command,
            "mean": benchmark.get("time_wall_clock_mean", benchmark.get("mean")),
            "stddev": benchmark.get("time_wall_clock_stddev", benchmark.get("stddev")),
            "median": benchmark.get("time_wall_clock_median", benchmark.get("median")),
            "user": benchmark.get("user", ""),
            "system": benchmark.get("system", ""),
            "min": benchmark.get("time_wall_clock_min", benchmark.get("min")),
            "max": benchmark.get("time_wall_clock_max", benchmark.get("max")),
        })

consolidate = pd.DataFrame(rows)
if consolidate.empty:
    raise RuntimeError("No benchmark CSV files were found")

consolidate["date"] = pd.to_datetime(consolidate["date"])
consolidate.sort_values("date", inplace=True)
consolidate.to_csv("results.csv", index=False)
consolidate.to_csv("results-sorted.csv", index=False)
print(consolidate.head())
