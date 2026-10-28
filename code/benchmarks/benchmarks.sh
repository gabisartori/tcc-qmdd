set -e
LOG_FILE="results/$(date +%FT%X)-benchmarks.log"


log() {
  echo "[$(date +%FT%X)] $1" >> $LOG_FILE
}

# simulator algorithm n_qubits
bench() {
  log "Benchmarking $2 with $1 qubits and $3 simulator..."
  hyperfine -w 5 -r 10 --export-csv "results/$(date +%FT%X)-$1-$2-$3.csv" "python3 benchmarks/$2.py $1 $3"
}

# This function slowly grows the number of qubits until the benchmark times out.
# As the time taken to benchmark increases with the number of qubits
# this function will use less runs since there variance is less important for larger execution times.
bench_until() {
  local method=$1
  local algorithm=$2
  local n_qubits=$3 # Initial number of qubits to start benchmarking with
  local max_time=$4

  log "Benchmarking $method $algorithm starting at $n_qubits qubits for a maximum of ${max_time}s..."

  while true; do
    log "Benchmarking $method $algorithm with $n_qubits qubits..."
    # Decrease number of runs for larger qubit counts to avoid needlessly long benchmarking times
    if [ $n_qubits -lt 8 ]; then
      warmup=15
      runs=30
    elif [ $n_qubits -lt 16 ]; then
      warmup=10
      runs=20
    elif [ $n_qubits -lt 20 ]; then
      warmup=5
      runs=10
    else
      warmup=3
      runs=5
    fi

    # Run hyperfine with a timeout. If it times out, log the event and break the loop.
    if ! timeout "${max_time}s" \
      hyperfine -w 5 -r $runs --export-csv "results/$(date +%FT%X)-$method-$algorithm-$n_qubits.csv" \
      "python3 benchmarks/$algorithm.py $method $n_qubits"; then
        log "Benchmarking $method $algorithm with $n_qubits qubits timed out after ${max_time}s."
        break
    fi
    ((n_qubits++))
  done 
}

# bench_until simulator algorithm n_qubits max_time(s)
for method in qmdd dense sparse; do
  for params in "grover 1" "qpe 2" "falqon 3"; do
    read algorithm n_qubits <<< "$params"
    bench_until $method $algorithm $n_qubits 3600
  done
done
