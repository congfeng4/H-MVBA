#!/bin/bash
# Script to reproduce experiments from the paper
# "Faster Hash-based Multi-valued Validated Asynchronous Byzantine Agreement"
# Runs H-MVBA, Dumbo-MVBA*, and FIN-MVBA with various N and batch sizes.

set -e  # exit on error

# Configuration
# Network sizes as in paper
N_VALUES=(6 16 31 61 101 201)
# Batch sizes (B) where each transaction is 250 bytes, input size L = 250 * B
# Paper uses B from 0 (empty string) to 7×10^3
B_VALUES=(0 10 100 1000 7000)
# Protocols to test
PROTOCOLS=("hmvba" "dumbomvbastar" "finmvba")
# Number of repetitions (one-shot agreements) K
K=10
# Warm-up count C (excluded from metrics)
C=0
# Output directory
RESULTS_DIR="paper_results"
# Parse script
PARSE_SCRIPT="parse_metrics.py"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Determine f for each protocol and N
# H-MVBA tolerates f < n/5 (20%)
# Dumbo-MVBA* and FIN-MVBA tolerate f < n/3
compute_f() {
    local n=$1
    local protocol=$2
    if [[ "$protocol" == "hmvba" ]]; then
        # floor((n-1)/5)
        echo $(( (n-1) / 5 ))
    else
        # floor((n-1)/3)
        echo $(( (n-1) / 3 ))
    fi
}

# Loop over all configurations
for protocol in "${PROTOCOLS[@]}"; do
    for N in "${N_VALUES[@]}"; do
        f=$(compute_f $N $protocol)
        if [[ $f -lt 1 ]]; then
            echo "Skipping N=$N with protocol $protocol because f=$f < 1"
            continue
        fi
        for B in "${B_VALUES[@]}"; do
            echo "=== Running $protocol N=$N f=$f B=$B K=$K C=$C ==="
            # Create experiment directory
            EXP_DIR="$RESULTS_DIR/${protocol}_N${N}_f${f}_B${B}_K${K}_C${C}"
            mkdir -p "$EXP_DIR"
            # Copy hosts.config if needed (local testing uses default)
            # Run the test
            bash run_local_network_mvba_test.sh $N $f $B $K $C $protocol
            # Wait a bit for processes to clean up
            sleep 5
            # Move logs to experiment directory
            mv verbose_log "$EXP_DIR/"
            mv log "$EXP_DIR/"
            # Parse metrics
            cd "$EXP_DIR"
            python3 ../$PARSE_SCRIPT verbose_log > summary.txt
            # Also generate CSV
            python3 ../$PARSE_SCRIPT verbose_log metrics.csv
            cd - > /dev/null
            echo "Results saved to $EXP_DIR"
        done
    done
done

echo "All experiments completed."