# Progress Log

## Session Start: 2026-02-08
Goal: Reproduce experiments from "Faster Hash-based Multi-valued Validated Asynchronous Byzantine Agreement"

### 2026-02-08 (Initial)
- Read existing test scripts (`test_hmvba.sh`, `test_dumbomvbastar.sh`, `test_finmvba.sh`)
- Examined `run_local_network_mvba_test.sh` core script
- Examined `run_socket_mvba_node.py` entry point
- Created metric parsing script `parse_metrics.py`
- Created experiment runner script `reproduce_paper.sh`
- Created planning files (`task_plan.md`, `findings.md`, `progress.md`)
- Ran session catchup script (no unsynced context found)

### Next Actions
1. Verify environment (Docker or local)
2. Run a small test to confirm scripts work
3. Begin Phase 1 of task plan

### 2026-02-08 (Phase 1 Start)
- Marked Phase 1 as in progress in task_plan.md
- Starting environment verification
- Docker container is running (docker-env-1)
- Verified Python packages (gevent, numpy, etc.)
- Ran `test_hmvba.sh` inside container - success, metrics obtained:
  - Latency: 0.060052s, TPS: 166.523236 for N=6, B=10, K=1
- Fixed pycrypto Python 2 syntax error in posix.py (changed `except IOError, e:` to `except IOError as e:`)
- Installed pycryptodome as replacement for pycrypto
- Ran `test_dumbomvbastar.sh` - success after key generation fix
- Ran `test_finmvba.sh` - success
- Verified metric parsing script `parse_metrics.py` works
- **Phase 1 completed**

### 2026-02-08 (Phase 2: Design Experiment Matrix)
- Created `generate_experiment_matrix.py` to generate parameter combinations
- Computed fault tolerance: H-MVBA (f < n/5), others (f < n/3)
- Generated `experiment_matrix.csv` and `experiment_matrix.md` with 90 configurations (3 protocols × 6 N values × 5 B values)
- Each experiment runs K=10 repetitions, C=0 warm-up
- **Phase 2 completed**

### 2026-02-08 (Phase 3: Implement Automated Experiment Runner)
- Created `run_experiments.py` with subprocess management, timeout handling, and process group killing
- Fixed assertion error for B=0 in node.py, dumbo_node.py, speedmvba nodes
- Fixed path resolution for parse_metrics.py (use absolute paths)
- Added debugging output and real-time logging
- Verified runner works with single experiment (hmvba_N6_f1_B10_K10_C0) - success
- **Phase 3 completed**

### 2026-02-08 (Phase 4: Run Experiments Batch 1 - Started)
- Ready to run experiments for N = 6, 16, 31 (all protocols, all B)
- Will use `run_experiments.py` with skip-completed flag to resume
- Estimated runtime: ~2.5 hours for first batch (30 experiments)
- Monitor logs for failures