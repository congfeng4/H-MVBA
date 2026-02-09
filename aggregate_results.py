#!/usr/bin/env python3
"""
Aggregate results from paper experiments.
Reads summary.txt and experiment.log files from paper_results/ directories.
Outputs CSV with aggregated metrics for analysis.
"""

import os
import json
import csv
import re
from pathlib import Path

RESULTS_DIR = "paper_results"
OUTPUT_CSV = "aggregated_results.csv"
OUTPUT_SUMMARY = "experiment_summary.md"

def parse_directory_name(dir_name):
    """Parse experiment parameters from directory name.
    Format: {protocol}_N{N}_f{f}_B{B}_K{K}_C{C}
    Returns dict or None if pattern doesn't match.
    """
    pattern = r'^([a-zA-Z0-9]+)_N(\d+)_f(\d+)_B(\d+)_K(\d+)_C(\d+)$'
    match = re.match(pattern, dir_name)
    if not match:
        return None
    
    protocol = match.group(1)
    N = int(match.group(2))
    f = int(match.group(3))
    B = int(match.group(4))
    K = int(match.group(5))
    C = int(match.group(6))
    input_bytes = 250 * B  # each transaction is 250 bytes
    
    return {
        'protocol': protocol,
        'N': N,
        'f': f,
        'B': B,
        'K': K,
        'C': C,
        'input_bytes': input_bytes,
    }

def parse_summary_txt(filepath):
    """Parse summary.txt file, extract JSON summary.
    Returns dict with metrics or None if parsing fails.
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        # Find JSON part (after "JSON summary:")
        json_start = content.find('{')
        if json_start == -1:
            return None
        json_str = content[json_start:]
        data = json.loads(json_str)
        return data
    except Exception as e:
        print(f"Warning: Failed to parse {filepath}: {e}")
        return None

def parse_experiment_log(filepath):
    """Parse experiment.log file for runtime and success status.
    Returns dict with runtime, success flag, and any other metadata.
    """
    result = {
        'success': False,
        'runtime_seconds': None,
        'timeout': False,
    }
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith('Success:'):
                success_str = line.split(':')[1].strip()
                result['success'] = success_str.lower() == 'true'
            elif line.startswith('Elapsed:'):
                # Format: "Elapsed: 159.5s"
                elapsed_str = line.split(':')[1].strip()
                if elapsed_str.endswith('s'):
                    elapsed_str = elapsed_str[:-1]
                try:
                    result['runtime_seconds'] = float(elapsed_str)
                except ValueError:
                    pass
            elif 'Timeout' in line:
                result['timeout'] = True
    except Exception as e:
        print(f"Warning: Failed to parse {filepath}: {e}")
    
    return result

def main():
    results_dir = Path(RESULTS_DIR)
    if not results_dir.exists():
        print(f"Error: Results directory {RESULTS_DIR} not found.")
        return
    
    # Collect all experiment directories
    experiments = []
    for item in results_dir.iterdir():
        if item.is_dir():
            params = parse_directory_name(item.name)
            if not params:
                print(f"Warning: Could not parse directory name: {item.name}")
                continue
            
            # Check for summary.txt
            summary_file = item / 'summary.txt'
            metrics = None
            if summary_file.exists():
                metrics = parse_summary_txt(summary_file)
            
            # Check for experiment.log
            log_file = item / 'experiment.log'
            log_info = {}
            if log_file.exists():
                log_info = parse_experiment_log(log_file)
            
            # Combine all data
            exp_data = {
                **params,
                'has_summary': metrics is not None,
                'has_log': log_file.exists(),
                **log_info,
            }
            
            if metrics:
                exp_data.update(metrics)
            
            experiments.append(exp_data)
    
    print(f"Found {len(experiments)} experiment directories.")
    
    # Write CSV
    csv_columns = [
        'protocol', 'N', 'f', 'B', 'K', 'C', 'input_bytes',
        'success', 'timeout', 'runtime_seconds',
        'has_summary', 'has_log',
        'num_nodes', 'total_tx',
        'latency_mean', 'latency_std',
        'tps_mean', 'tps_std',
    ]
    
    with open(OUTPUT_CSV, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for exp in experiments:
            # Ensure all columns present
            row = {col: exp.get(col, '') for col in csv_columns}
            writer.writerow(row)
    
    print(f"CSV written to {OUTPUT_CSV}")
    
    # Generate summary markdown
    generate_summary_md(experiments)

def generate_summary_md(experiments):
    """Generate markdown summary of experiment results."""
    # Count by protocol
    protocol_counts = {}
    success_counts = {}
    timeout_counts = {}
    
    for exp in experiments:
        protocol = exp['protocol']
        protocol_counts[protocol] = protocol_counts.get(protocol, 0) + 1
        if exp.get('success'):
            success_counts[protocol] = success_counts.get(protocol, 0) + 1
        if exp.get('timeout'):
            timeout_counts[protocol] = timeout_counts.get(protocol, 0) + 1
    
    with open(OUTPUT_SUMMARY, 'w') as f:
        f.write("# Experiment Results Summary\n\n")
        f.write(f"Total experiments: {len(experiments)}\n\n")
        
        f.write("## By Protocol\n")
        f.write("| Protocol | Total | Successful | Timeouts | Success Rate |\n")
        f.write("|----------|-------|------------|----------|--------------|\n")
        for protocol in sorted(protocol_counts.keys()):
            total = protocol_counts[protocol]
            successful = success_counts.get(protocol, 0)
            timeouts = timeout_counts.get(protocol, 0)
            rate = (successful / total * 100) if total > 0 else 0
            f.write(f"| {protocol} | {total} | {successful} | {timeouts} | {rate:.1f}% |\n")
        
        f.write("\n## By Network Size (N)\n")
        # Group by N
        n_counts = {}
        n_success = {}
        for exp in experiments:
            n = exp['N']
            n_counts[n] = n_counts.get(n, 0) + 1
            if exp.get('success'):
                n_success[n] = n_success.get(n, 0) + 1
        
        f.write("| N | Total | Successful | Success Rate |\n")
        f.write("|---|-------|------------|--------------|\n")
        for n in sorted(n_counts.keys()):
            total = n_counts[n]
            successful = n_success.get(n, 0)
            rate = (successful / total * 100) if total > 0 else 0
            f.write(f"| {n} | {total} | {successful} | {rate:.1f}% |\n")
        
        # List failed experiments
        failed = [exp for exp in experiments if not exp.get('success')]
        if failed:
            f.write("\n## Failed Experiments\n")
            f.write("| Protocol | N | f | B | K | C | Reason |\n")
            f.write("|----------|---|---|---|---|---|--------|\n")
            for exp in failed:
                reason = "Timeout" if exp.get('timeout') else "Unknown"
                f.write(f"| {exp['protocol']} | {exp['N']} | {exp['f']} | {exp['B']} | {exp['K']} | {exp['C']} | {reason} |\n")
        
        # Successful experiments with metrics
        successful = [exp for exp in experiments if exp.get('has_summary')]
        if successful:
            f.write("\n## Successful Experiments Metrics Overview\n")
            f.write("| Protocol | N | B | Latency (mean±std) | TPS (mean±std) |\n")
            f.write("|----------|---|---|-------------------|----------------|\n")
            # Show one per protocol/B combination for brevity
            shown = set()
            for exp in sorted(successful, key=lambda x: (x['protocol'], x['N'], x['B'])):
                key = (exp['protocol'], exp['N'], exp['B'])
                if key in shown:
                    continue
                shown.add(key)
                latency = f"{exp.get('latency_mean', 0):.4f}±{exp.get('latency_std', 0):.4f}"
                tps = f"{exp.get('tps_mean', 0):.1f}±{exp.get('tps_std', 0):.1f}"
                f.write(f"| {exp['protocol']} | {exp['N']} | {exp['B']} | {latency} | {tps} |\n")
    
    print(f"Summary written to {OUTPUT_SUMMARY}")

if __name__ == '__main__':
    main()