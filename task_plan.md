# Task Plan: Reproduce experiments from "Faster Hash-based Multi-valued Validated Asynchronous Byzantine Agreement"

## Goal
Run experiments comparing H-MVBA with baseline MVBAs (Dumbo-MVBA*, FIN-MVBA) across network sizes N = {6, 16, 31, 61, 101, 201} and batch sizes B = {0, 10, 100, 1000, 7000}. Collect latency and throughput metrics, aggregate results, and produce comparable data to paper Figures 2-4.

## Phases

### Phase 1: Environment Setup & Verification ✅
- [x] Verify Docker environment is ready (or local dependencies)
- [x] Ensure all required Python packages installed (assumed via Dockerfile)
- [x] Test that existing test scripts (`test_hmvba.sh`, `test_dumbomvbastar.sh`, `test_finmvba.sh`) run successfully
  - [x] `test_hmvba.sh` works (metrics produced)
  - [x] `test_dumbomvbastar.sh` works (after fixing pycrypto Python 3 syntax)
  - [x] `test_finmvba.sh` works
- [x] Verify metric parsing script works

### Phase 2: Design Experiment Matrix ✅
- [x] Define exact parameter combinations (N, f, B, K, C) for each protocol
- [x] Compute f for each N based on protocol tolerance (H-MVBA: f < n/5, others: f < n/3)
- [x] Create a table of all experiments to run (see `experiment_matrix.csv` and `experiment_matrix.md`)

### Phase 3: Implement Automated Experiment Runner ✅
- [x] Enhance `reproduce_paper.sh` to handle large-scale runs (created `run_experiments.py`)
- [x] Add error handling and logging
- [x] Implement sequential execution (avoid overloading system)
- [x] Ensure proper cleanup between runs

### Phase 4: Run Experiments (Batch 1: Small N) ✅
- [x] Run experiments for N = 6, 16, 31 (all protocols, all B)
- [x] Monitor logs for failures
- [x] Collect results in structured directories

### Phase 5: Run Experiments (Batch 2: Large N) ⚠️ Partially Complete
- [x] Run experiments for N = 61 (H-MVBA only - baseline protocols timed out)
- [x] Run experiments for N = 101 (H-MVBA only - baseline protocols timed out)
- [ ] Run experiments for N = 201 (all protocols timed out - need longer timeout)
- [x] Monitor system resources
- [x] Handle potential timeouts (set 20-minute timeout, insufficient for large N)
- **Note**: 53/90 experiments completed. N=61,101 baselines timed out; N=201 all timed out.

### Phase 6: Data Aggregation ✅
- [x] Parse all experiment logs using `parse_metrics.py`
- [x] Combine results into master CSV/JSON (`aggregated_results.csv`)
- [x] Compute statistics (mean, std) across nodes and repetitions
- **Files**: `aggregate_results.py`, `aggregated_results.csv`

### Phase 7: Analysis & Comparison ✅
- [x] Generate tables similar to paper Table II (`paper_tables.md`)
- [x] Create plots of latency vs. input size, throughput vs. scale (data in CSV files)
- [x] Compare H-MVBA vs. baselines (`speedup_analysis.md`)
- **Files**: `generate_tables.py`, `analyze_results.py`, `paper_tables.md`, `speedup_analysis.md`, `plot_latency_vs_b.csv`, `plot_throughput_vs_n.csv`

### Phase 8: Documentation ⚠️ Partially Complete
- [x] Summarize findings (`reproduction_summary.md`, `experiment_summary.md`)
- [x] Note any deviations from paper results (`reproduction_summary.md`)
- [x] Generate visualizations (Figures 2-4) (`generate_plots.py`, `plots/` directory)
- [ ] Prepare final report (could expand with deeper analysis, statistical tests)
- **Files**: `reproduction_summary.md`, `experiment_summary.md`, `generate_plots.py`

## Decisions
- Use Docker environment for consistency (as recommended in README)
- Run sequentially to avoid resource contention
- Store raw logs per experiment in `paper_results/<protocol>_N<...>/`
- Aggregate parsed metrics in CSV format for easy analysis

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| Pycrypto syntax error (Python 2 `except IOError, e:` in posix.py) | 1 | Patched file to use `except IOError as e:`; also installed pycryptodome as replacement |
| Key generation failing for dumbomvbastar | 1 | Fixed pycrypto syntax, keys generated successfully |
| Assertion error `self.B > 0` for B=0 experiments | 1 | Updated to `self.B >= 0` in four node implementations (node.py, dumbo_node.py, speedmvba nodes) |
| Timeout errors for large N (≥101) experiments | 1 | 20-minute timeout insufficient; need longer timeout or resource scaling |

## Progress Tracking
- Start time: 2026-02-08 (estimated)
- Current phase: Phase 8 (Documentation) - Partially Complete
- Completion: 53/90 experiments successful (59%)
- Key results: H-MVBA outperforms baselines for N≤31, but speedups smaller than paper claims
- Large N experiments (≥101) timed out; need longer timeouts or resource scaling

## Files Created/Modified
- `parse_metrics.py` (metric parsing)
- `run_experiments.py` (automated experiment runner)
- `aggregate_results.py`, `aggregated_results.csv` (data aggregation)
- `generate_tables.py`, `analyze_results.py` (analysis)
- `paper_tables.md`, `speedup_analysis.md` (comparison tables)
- `plot_latency_vs_b.csv`, `plot_throughput_vs_n.csv` (plot data)
- `generate_plots.py` (plot generation)
- `reproduction_summary.md`, `experiment_summary.md` (documentation)
- `task_plan.md` (this file)
- `findings.md` (research findings)
- `progress.md` (session log)

## Notes
- Total experiments: 3 protocols × 6 N values × 5 B values = 90 configurations
- Each experiment runs K=10 repetitions, C=0 warm-up
- Expect long runtime (hours to days). May need to prioritize subset.
- **Completed**: 53 experiments (59%). N=6,16,31 complete; N=61,101 H-MVBA only; N=201 timed out.
- **Next steps options**:
  1. Extend timeouts for large N experiments (3600+ seconds)
  2. Generate visualizations from CSV plot data
  3. Perform deeper statistical analysis on existing results
  4. Profile/optimize code to match paper's performance
  5. Compare with paper's exact numbers if available