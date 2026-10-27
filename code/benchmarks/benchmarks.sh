bench() {
	hyperfine -w 5 -r 10 -u millisecond --export-csv "results/$(date +%F)-$1-$2-$3.csv" "python3 benchmarks/grover.py $1 $3 1"
}

bench qmdd grover 1
bench qmdd grover 2
bench qmdd grover 4
bench qmdd grover 8
bench qmdd grover 12
bench qmdd grover 16
bench qmdd grover 20

