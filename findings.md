# Findings

## Paper Details
- Title: "Faster Hash-based Multi-valued Validated Asynchronous Byzantine Agreement"
- Authors: Hanwen Feng, Zhenliang Lu, Tiancheng Mai, Qiang Tang
- Published: DSN 2025
- Compares H-MVBA (hash-based) with baselines: Dumbo-MVBA*, FIN-MVBA, sMVBA*-BLS, sMVBA*-ECDSA, FLT24-MVBA, KNR24-MVBA
- Key metrics: Latency (seconds), Throughput (TPS)
- Network sizes tested: N = 6, 16, 31, 61, 101, 201
- Input sizes: L = 250×B bytes, where B ∈ {0, 10, 100, 1000, 7000} (transactions of 250 bytes each)
- Fault tolerance: H-MVBA tolerates f < n/5 (20%); others f < n/3 (33%)
- Experiments conducted on AWS EC2 t2.medium instances across 13 regions

## Codebase Structure
- Forked from Dumbo-NG (https://github.com/yylluu/Dumbo_NG)
- Includes implementations of:
  - `hmvba` (H-MVBA) in `hash_mvba/core/hmvba_protocol.py`
  - `dumbomvbastar` (Dumbo-MVBA*) in `dumbomvbastar/core/dumbomvba_star.py`
  - `finmvba` (FIN-MVBA) in `fin_mvba/core/fin_mvba_protocol.py`
  - Also has `speedmvba` and `speedmvba_bls` directories (not used in current test scripts)
- Entry point: `run_socket_mvba_node.py`
- Test script: `run_local_network_mvba_test.sh` launches N nodes
- Existing test scripts:
  - `test_hmvba.sh`: N=6, f=1, B=10, K=1, C=0, protocol=hmvba
  - `test_dumbomvbastar.sh`: similar for dumbomvbastar
  - `test_finmvba.sh`: similar for finmvba

## Metric Collection
- Each node outputs metrics to stdout, captured in `verbose_log/<node>.stdout.log`
- Metric line format: `node: 0 epoch: 1 run: 0.059161, total delivered Txs after warm-up: 10, latency after warm-up: 0.059161, tps after warm-up: 169.031104, average latency by rounds + stddev: 0.059161 0.000000, average tps by rounds + stddev: 169.031104 0.000000,`
- Latency measured in seconds, throughput in transactions per second (TPS)
- Warm-up rounds excluded from metrics (parameter C)

## Environment
- Docker environment recommended (see `docker/` directory)
- Dependencies: Python 3, gevent, numpy, ecdsa, pysocks, gmpy2, zfec, gipc, pycrypto, coincurve, PBC library, Charm crypto library
- Hosts configuration: `hosts.config` file maps node IDs to IPs/ports; for local testing uses `localhost` with port offsets

## Key Parameters
- `--N`: number of parties
- `--f`: number of faulty parties (adversaries)
- `--B`: batch size (number of transactions per input)
- `--K`: number of one-shot agreements to repeat
- `--C`: warm-up count (excluded from metrics)
- `--P`: protocol (`hmvba`, `dumbomvbastar`, `finmvba`)

## Parsing Script
Created `parse_metrics.py` that:
- Reads all `verbose_log/*.stdout.log` files
- Extracts latency, TPS, total transactions
- Computes mean and standard deviation across nodes
- Outputs CSV and JSON summary

## Experiment Runner Script
Created `reproduce_paper.sh` that:
- Loops over protocols, N values, B values
- Computes appropriate f for each protocol
- Runs `run_local_network_mvba_test.sh` with parameters
- Moves logs to organized directory `paper_results/<protocol>_N<N>_f<f>_B<B>_K<K>_C<C>/`
- Runs parsing script to generate summary

## Known Issues
- Need to ensure Docker environment is running (or install dependencies locally)
- The scripts kill all python3 processes before starting (`killall --quiet python3`), which could interfere with other processes
- For Dumbo-MVBA*, key generation required (`run_trusted_key_gen.py`) - handled in `run_local_network_mvba_test.sh` line 19-23
- Large N (201) may cause resource exhaustion; need to monitor
- Experiments may take a long time (90 configurations × each with 10 repetitions)

## Experiment Results & Analysis
- **Success rate**: 53/90 experiments completed (59%)
- **H-MVBA performance**: Outperforms baselines for N≤31, but speedups smaller than paper claims:
  - vs Dumbo-MVBA*: up to 1.54× lower latency (paper claims 2.5×)
  - vs FIN-MVBA: up to 3.95× lower latency (paper claims 11.7×)
- **FIN-MVBA strength**: Shows strong performance for small batch sizes at N=6
- **Scalability limits**: Baseline protocols time out for N≥61; H-MVBA scales better
- **Timeout issues**: 20-minute timeout insufficient for large N (≥101) experiments
- **Data available**: `aggregated_results.csv` contains all successful experiment metrics
- **Analysis files**: `paper_tables.md`, `speedup_analysis.md`, `reproduction_summary.md`