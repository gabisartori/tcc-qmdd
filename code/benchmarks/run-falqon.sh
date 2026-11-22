set -e
OUTPUT_DIR="results/falqon/$(date +%FT%X)"
mkdir -p $OUTPUT_DIR
LOG_FILE="$OUTPUT_DIR/$(date +%FT%X)-benchmarks.log"


log() {
  echo "[$(date +%FT%X)] $1" >> $LOG_FILE
}

# This function slowly grows the number of qubits until the benchmark times out.
# As the time taken to benchmark increases with the number of qubits
# this function will use less runs since there variance is less important for larger execution times.
bench_until() {
  local method=$1
  local n_qubits=$2 # Fixed number of qubits to benchmark with
  local n_layers=$3 # Initial number of layers to start benchmarking with
  local max_time=$4

  log "Benchmarking $method $algorithm starting at $n_qubits qubits for a maximum of ${max_time}s..."

  while true; do
    log "Benchmarking $method $algorithm with $n_qubits qubits and $n_layers layers..."
    # Decrease number of runs for larger qubit counts to avoid needlessly long benchmarking times
    if [ $n_layers -lt 100 ]; then
      warmup=15
      runs=30
    elif [ $n_layers -lt 1000 ]; then
      warmup=2
      runs=3
    fi
    warmup=1
    runs=1

    # Run hyperfine with a timeout. If it times out, log the event and break the loop.
    if ! timeout "${max_time}s" \
      hyperfine -w $warmup -r $runs --export-csv "$OUTPUT_DIR/$(date +%FT%X)-$method-$n_qubits-$n_layers.csv" \
      "python3 benchmarks/falqon.py $method $n_qubits $n_layers"; then
        log "Benchmarking $method $algorithm with $n_qubits qubits and $n_layers layers timed out after ${max_time}s."
        break
    fi
    n_layers=$((n_layers + 10))
  done 
}

TIMEOUT=30 # $((5*60*60))
N_QUBITS=18

# bench_until simulator algorithm n_qubits max_time(s)
for method in qmdd dense sparse; do
  bench_until $method $N_QUBITS 10 $TIMEOUT
done
