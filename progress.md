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