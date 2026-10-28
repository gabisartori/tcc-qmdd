# simulator algorithm n_qubits
bench() {
  case $2 in
    grover)
      script="benchmarks/grover.py"
      ;;
    qpe)
      script="benchmarks/qpe.py"
      ;;
    falqon)
      script="benchmarks/falqon.py"
      ;;
    *)
      echo "Unknown algorithm: $2"
      exit 1
      ;;
  esac
  hyperfine -w 5 -r 10 --export-csv "results/$(date +%FT%X)-$1-$2-$3.csv" "python3 $script $1 $3"
}

bench qmdd grover 1
bench qmdd grover 2
bench qmdd grover 4
bench qmdd grover 8
bench qmdd grover 12
bench qmdd grover 16
bench qmdd falqon 4
bench qmdd falqon 8
bench qmdd falqon 12
bench qmdd falqon 16
bench qmdd qpe 2
bench qmdd qpe 4
bench qmdd qpe 8
bench qmdd qpe 12
bench qmdd qpe 16
