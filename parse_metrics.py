#!/usr/bin/env python3
"""
Parse metrics from verbose_log/*.stdout.log files.
Usage: python3 parse_metrics.py <log_directory>
Outputs CSV with aggregated metrics.
"""

import os, re, sys, statistics, csv, json
from pathlib import Path

def parse_stdout_file(filepath):
    """Parse a single stdout.log file, return dict of metrics."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    # We assume the metric line is the last line containing 'latency after warm-up'
    metric_line = None
    for line in lines:
        if 'latency after warm-up' in line:
            metric_line = line.strip()
            break
    if not metric_line:
        return None
    
    # regex to extract numbers
    # node: 0 epoch: 1 run: 0.059161, total delivered Txs after warm-up: 10, latency after warm-up: 0.059161, tps after warm-up: 169.031104, average latency by rounds + stddev: 0.059161 0.000000, average tps by rounds + stddev: 169.031104 0.000000,
    pattern = r'node:\s*(\d+).*?epoch:\s*(\d+).*?run:\s*([\d.]+).*?total delivered Txs after warm-up:\s*(\d+).*?latency after warm-up:\s*([\d.]+).*?tps after warm-up:\s*([\d.]+).*?average latency by rounds \+ stddev:\s*([\d.]+)\s+([\d.]+).*?average tps by rounds \+ stddev:\s*([\d.]+)\s+([\d.]+)'
    match = re.search(pattern, metric_line, re.DOTALL)
    if not match:
        # fallback simpler pattern
        match = re.search(r'node:\s*(\d+).*?latency after warm-up:\s*([\d.]+).*?tps after warm-up:\s*([\d.]+)', metric_line)
        if match:
            node = int(match.group(1))
            latency = float(match.group(2))
            tps = float(match.group(3))
            return {
                'node': node,
                'latency': latency,
                'tps': tps,
            }
        return None
    
    node = int(match.group(1))
    epoch = int(match.group(2))
    run_time = float(match.group(3))
    total_tx = int(match.group(4))
    latency = float(match.group(5))
    tps = float(match.group(6))
    avg_latency = float(match.group(7))
    std_latency = float(match.group(8))
    avg_tps = float(match.group(9))
    std_tps = float(match.group(10))
    
    return {
        'node': node,
        'epoch': epoch,
        'run_time': run_time,
        'total_tx': total_tx,
        'latency': latency,
        'tps': tps,
        'avg_latency': avg_latency,
        'std_latency': std_latency,
        'avg_tps': avg_tps,
        'std_tps': std_tps,
    }

def aggregate_metrics(log_dir):
    """Aggregate metrics across all nodes in log_dir."""
    log_dir = Path(log_dir)
    stdout_files = list(log_dir.glob('*.stdout.log'))
    if not stdout_files:
        # maybe inside verbose_log subdirectory
        verbose_dir = log_dir / 'verbose_log'
        if verbose_dir.exists():
            stdout_files = list(verbose_dir.glob('*.stdout.log'))
        else:
            # try parent directory
            parent = log_dir.parent
            if (parent / 'verbose_log').exists():
                stdout_files = list((parent / 'verbose_log').glob('*.stdout.log'))
    
    metrics = []
    for f in stdout_files:
        m = parse_stdout_file(f)
        if m:
            metrics.append(m)
    
    if not metrics:
        return {}
    
    # compute aggregates across nodes
    latencies = [m['latency'] for m in metrics]
    tpses = [m['tps'] for m in metrics]
    total_txs = [m.get('total_tx', 0) for m in metrics]
    # assume all nodes have same total_tx (should be)
    total_tx = total_txs[0] if total_txs else 0
    
    agg = {
        'num_nodes': len(metrics),
        'total_tx': total_tx,
        'latency_mean': statistics.mean(latencies),
        'latency_std': statistics.stdev(latencies) if len(latencies) > 1 else 0.0,
        'tps_mean': statistics.mean(tpses),
        'tps_std': statistics.stdev(tpses) if len(tpses) > 1 else 0.0,
        'node_metrics': metrics,
    }
    return agg

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_metrics.py <log_directory> [output.csv]")
        sys.exit(1)
    
    log_dir = sys.argv[1]
    agg = aggregate_metrics(log_dir)
    if not agg:
        print("No metrics found.")
        sys.exit(1)
    
    # print summary
    print(f"Nodes: {agg['num_nodes']}")
    print(f"Total transactions: {agg['total_tx']}")
    print(f"Average latency: {agg['latency_mean']:.6f} ± {agg['latency_std']:.6f}")
    print(f"Average TPS: {agg['tps_mean']:.6f} ± {agg['tps_std']:.6f}")
    
    # output CSV if requested
    if len(sys.argv) >= 3:
        output_csv = sys.argv[2]
        with open(output_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['node', 'latency', 'tps', 'total_tx', 'avg_latency', 'std_latency', 'avg_tps', 'std_tps'])
            for m in agg['node_metrics']:
                writer.writerow([
                    m['node'],
                    m.get('latency', ''),
                    m.get('tps', ''),
                    m.get('total_tx', ''),
                    m.get('avg_latency', ''),
                    m.get('std_latency', ''),
                    m.get('avg_tps', ''),
                    m.get('std_tps', ''),
                ])
        print(f"CSV written to {output_csv}")
    
    # also output JSON summary
    summary = {
        'num_nodes': agg['num_nodes'],
        'total_tx': agg['total_tx'],
        'latency_mean': agg['latency_mean'],
        'latency_std': agg['latency_std'],
        'tps_mean': agg['tps_mean'],
        'tps_std': agg['tps_std'],
    }
    print("\nJSON summary:")
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()