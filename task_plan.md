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

### Phase 3: Implement Automated Experiment Runner
- [x] Enhance `reproduce_paper.sh` to handle large-scale runs (created `run_experiments.py`)
- [-] Add error handling and logging (in progress)
- [ ] Implement sequential execution (avoid overloading system)
- [ ] Ensure proper cleanup between runs

### Phase 4: Run Experiments (Batch 1: Small N)
- [ ] Run experiments for N = 6, 16, 31 (all protocols, all B)
- [ ] Monitor logs for failures
- [ ] Collect results in structured directories

### Phase 5: Run Experiments (Batch 2: Large N)
- [ ] Run experiments for N = 61, 101, 201
- [ ] Monitor system resources
- [ ] Handle potential timeouts

### Phase 6: Data Aggregation
- [ ] Parse all experiment logs using `parse_metrics.py`
- [ ] Combine results into master CSV/JSON
- [ ] Compute statistics (mean, std) across nodes and repetitions

### Phase 7: Analysis & Comparison
- [ ] Generate tables similar to paper Table II
- [ ] Create plots of latency vs. input size, throughput vs. scale
- [ ] Compare H-MVBA vs. baselines

### Phase 8: Documentation
- [ ] Summarize findings
- [ ] Note any deviations from paper results
- [ ] Prepare final report

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

## Progress Tracking
- Start time: 2026-02-08 (estimated)
- Current phase: Phase 2 (Design Experiment Matrix)

## Files Created/Modified
- `parse_metrics.py` (already created)
- `reproduce_paper.sh` (already created)
- `task_plan.md` (this file)
- `findings.md` (to be created)
- `progress.md` (to be created)

## Notes
- Total experiments: 3 protocols × 6 N values × 5 B values = 90 configurations
- Each experiment runs K=10 repetitions, C=0 warm-up
- Expect long runtime (hours to days). May need to prioritize subset.