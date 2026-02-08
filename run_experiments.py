#!/usr/bin/env python3
"""
Run experiments from experiment matrix.
"""

import argparse
import csv
import os
import subprocess
import sys
import time
import signal
import shutil
from pathlib import Path

# Default parameters
RESULTS_DIR = "paper_results"
TIMEOUT_PER_EXPERIMENT = 600  # seconds (10 minutes)
PARSE_SCRIPT = "parse_metrics.py"

def run_command(cmd, cwd=None, timeout=None):
    """Run shell command with timeout, return (success, output)."""
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            timeout=timeout,
            capture_output=True,
            text=True
        )
        return proc.returncode == 0, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout} seconds"
    except Exception as e:
        return False, str(e)

def run_experiment(protocol, N, f, B, K, C, results_dir, timeout):
    """Run a single experiment."""
    # Create experiment directory name
    exp_name = f"{protocol}_N{N}_f{f}_B{B}_K{K}_C{C}"
    exp_dir = Path(results_dir) / exp_name
    exp_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"=== Starting experiment {exp_name} ===")
    
    # Clean up any existing logs in the main directory
    for d in ['verbose_log', 'log']:
        if Path(d).exists():
            shutil.rmtree(d)
        Path(d).mkdir()
    
    # Kill any leftover python3 processes (optional)
    # run_command("killall -9 python3 2>/dev/null; sleep 2")
    
    # Build command
    cmd = f"bash run_local_network_mvba_test.sh {N} {f} {B} {K} {C} {protocol}"
    print(f"Command: {cmd}")
    
    start_time = time.time()
    success, output = run_command(cmd, timeout=timeout)
    elapsed = time.time() - start_time
    
    # Move logs to experiment directory
    if Path('verbose_log').exists():
        shutil.move('verbose_log', exp_dir / 'verbose_log')
    if Path('log').exists():
        shutil.move('log', exp_dir / 'log')
    
    # Parse metrics
    parse_success = False
    metrics_summary = None
    if (exp_dir / 'verbose_log').exists():
        parse_cmd = f"python3 {PARSE_SCRIPT} verbose_log"
        parse_success, parse_output = run_command(parse_cmd, cwd=exp_dir)
        if parse_success:
            metrics_summary = parse_output
            with open(exp_dir / 'summary.txt', 'w') as f:
                f.write(parse_output)
            # Also generate CSV
            run_command(f"python3 {PARSE_SCRIPT} verbose_log metrics.csv", cwd=exp_dir)
        else:
            print(f"WARNING: Failed to parse metrics: {parse_output}")
    
    # Determine overall success
    overall_success = success and parse_success
    status = "SUCCESS" if overall_success else "FAILED"
    print(f"=== Experiment {exp_name} {status} (took {elapsed:.1f}s) ===")
    
    # Log experiment result
    with open(exp_dir / 'experiment.log', 'w') as f:
        f.write(f"Protocol: {protocol}\n")
        f.write(f"N: {N}, f: {f}, B: {B}, K: {K}, C: {C}\n")
        f.write(f"Command: {cmd}\n")
        f.write(f"Start time: {time.ctime(start_time)}\n")
        f.write(f"Elapsed: {elapsed:.1f}s\n")
        f.write(f"Success: {overall_success}\n")
        f.write("\n--- Command output ---\n")
        f.write(output)
        if metrics_summary:
            f.write("\n--- Metrics ---\n")
            f.write(metrics_summary)
    
    return overall_success

def main():
    parser = argparse.ArgumentParser(description="Run experiments from matrix CSV.")
    parser.add_argument('--matrix', default='experiment_matrix.csv',
                        help='CSV file with experiment matrix')
    parser.add_argument('--results', default=RESULTS_DIR,
                        help='Results directory')
    parser.add_argument('--timeout', type=int, default=TIMEOUT_PER_EXPERIMENT,
                        help='Timeout per experiment (seconds)')
    parser.add_argument('--skip-completed', action='store_true',
                        help='Skip experiments that already have results')
    parser.add_argument('--start', type=int, default=0,
                        help='Start from row index (0-based)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of experiments to run')
    args = parser.parse_args()
    
    # Read experiment matrix
    with open(args.matrix, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    total = len(rows)
    print(f"Loaded {total} experiments from {args.matrix}")
    
    # Create results directory
    Path(args.results).mkdir(exist_ok=True)
    
    # Run experiments
    success_count = 0
    for i, row in enumerate(rows[args.start:], start=args.start):
        if args.limit and (i - args.start) >= args.limit:
            print(f"Reached limit of {args.limit} experiments")
            break
        
        protocol = row['protocol']
        N = int(row['N'])
        f = int(row['f'])
        B = int(row['B'])
        K = int(row['K'])
        C = int(row['C'])
        
        exp_name = f"{protocol}_N{N}_f{f}_B{B}_K{K}_C{C}"
        exp_dir = Path(args.results) / exp_name
        
        # Skip if already completed and skip-completed flag set
        if args.skip_completed and (exp_dir / 'summary.txt').exists():
            print(f"Skipping already completed experiment {exp_name}")
            continue
        
        # Run experiment
        ok = run_experiment(protocol, N, f, B, K, C, args.results, args.timeout)
        if ok:
            success_count += 1
        
        # Brief pause between experiments
        time.sleep(2)
    
    print(f"\n=== Summary ===")
    print(f"Total experiments run: {len(rows)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(rows) - success_count}")
    print(f"Results saved in {args.results}/")

if __name__ == '__main__':
    main()