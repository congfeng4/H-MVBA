#!/usr/bin/env python3
"""
Generate comparison tables from aggregated results.
"""

import csv
import math
from pathlib import Path

INPUT_CSV = "aggregated_results.csv"
OUTPUT_MD = "paper_tables.md"

def load_successful_experiments():
    """Load successful experiments from CSV."""
    experiments = []
    with open(INPUT_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only include successful experiments with metrics
            if row.get('success', '').lower() == 'true' and row.get('has_summary', '').lower() == 'true':
                # Convert numeric fields
                row['N'] = int(row['N'])
                row['f'] = int(row['f'])
                row['B'] = int(row['B'])
                row['K'] = int(row['K'])
                row['C'] = int(row['C'])
                row['input_bytes'] = int(row['input_bytes'])
                if row['latency_mean']:
                    row['latency_mean'] = float(row['latency_mean'])
                    row['latency_std'] = float(row['latency_std'])
                    row['tps_mean'] = float(row['tps_mean'])
                    row['tps_std'] = float(row['tps_std'])
                    row['num_nodes'] = int(row['num_nodes'])
                    row['total_tx'] = int(row['total_tx'])
                    experiments.append(row)
    return experiments

def format_latency(latency_mean, latency_std):
    """Format latency as mean ± std."""
    if latency_mean < 0.001:
        return f"{latency_mean*1000:.2f}±{latency_std*1000:.2f} ms"
    elif latency_mean < 1:
        return f"{latency_mean*1000:.1f}±{latency_std*1000:.1f} ms"
    else:
        return f"{latency_mean:.3f}±{latency_std:.3f} s"

def format_tps(tps_mean, tps_std):
    """Format TPS appropriately."""
    if tps_mean < 1:
        return f"{tps_mean:.3f}±{tps_std:.3f}"
    elif tps_mean < 10:
        return f"{tps_mean:.2f}±{tps_std:.2f}"
    elif tps_mean < 100:
        return f"{tps_mean:.1f}±{tps_std:.1f}"
    else:
        # Round to integer for large values
        return f"{int(tps_mean)}±{int(tps_std)}"

def generate_table_similar_to_paper(experiments):
    """Generate table similar to paper Table II."""
    # Sort by protocol, N, B
    experiments.sort(key=lambda x: (x['protocol'], x['N'], x['B']))
    
    table_lines = []
    table_lines.append("# Table II: Performance Comparison (Partial Reproduction)\n")
    table_lines.append("| Protocol | N | f | B | Input (KB) | Latency (s) | Throughput (tx/s) |")
    table_lines.append("|----------|---|---|---|------------|-------------|-------------------|")
    
    for exp in experiments:
        # Skip B=0 (no input)
        if exp['B'] == 0:
            continue
        
        protocol = exp['protocol']
        N = exp['N']
        f = exp['f']
        B = exp['B']
        input_kb = exp['input_bytes'] / 1024
        latency = f"{exp['latency_mean']:.3f}±{exp['latency_std']:.3f}"
        tps = format_tps(exp['tps_mean'], exp['tps_std'])
        
        table_lines.append(f"| {protocol} | {N} | {f} | {B} | {input_kb:.1f} | {latency} | {tps} |")
    
    return "\n".join(table_lines)

def generate_protocol_comparison(experiments):
    """Generate comparison table for H-MVBA vs baselines for N=6,16,31."""
    # Filter for N in [6,16,31]
    filtered = [e for e in experiments if e['N'] in [6,16,31]]
    
    # Group by (N, B)
    groups = {}
    for exp in filtered:
        key = (exp['N'], exp['B'])
        if key not in groups:
            groups[key] = {}
        groups[key][exp['protocol']] = exp
    
    table_lines = []
    table_lines.append("# Protocol Comparison (N=6,16,31)\n")
    table_lines.append("| N | B | Protocol | Latency (s) | Throughput (tx/s) |")
    table_lines.append("|---|---|----------|-------------|-------------------|")
    
    for (N, B) in sorted(groups.keys()):
        if B == 0:
            continue
        group = groups[(N, B)]
        # Add a row for each protocol
        for protocol in ['hmvba', 'dumbomvbastar', 'finmvba']:
            if protocol in group:
                exp = group[protocol]
                latency = f"{exp['latency_mean']:.3f}±{exp['latency_std']:.3f}"
                tps = format_tps(exp['tps_mean'], exp['tps_std'])
                table_lines.append(f"| {N} | {B} | {protocol} | {latency} | {tps} |")
        # Add empty row for separation between different (N,B)
        table_lines.append("|---|---|----------|-------------|-------------------|")
    
    # Remove last separator
    if table_lines[-1].startswith('|---|---'):
        table_lines.pop()
    
    return "\n".join(table_lines)

def generate_scalability_table(experiments):
    """Generate table showing scalability with N for each protocol (fixed B=1000)."""
    # Filter for B=1000 (medium batch size)
    filtered = [e for e in experiments if e['B'] == 1000]
    
    table_lines = []
    table_lines.append("# Scalability with Network Size (B=1000)\n")
    table_lines.append("| Protocol | N | f | Latency (s) | Throughput (tx/s) |")
    table_lines.append("|----------|---|---|-------------|-------------------|")
    
    # Sort by protocol, N
    filtered.sort(key=lambda x: (x['protocol'], x['N']))
    
    for exp in filtered:
        protocol = exp['protocol']
        N = exp['N']
        f = exp['f']
        latency = f"{exp['latency_mean']:.3f}±{exp['latency_std']:.3f}"
        tps = format_tps(exp['tps_mean'], exp['tps_std'])
        table_lines.append(f"| {protocol} | {N} | {f} | {latency} | {tps} |")
    
    return "\n".join(table_lines)

def generate_speedup_table(experiments):
    """Compute speedup of H-MVBA over baselines."""
    # Only consider N where all three protocols have data
    n_values = set()
    protocol_data = {}
    for exp in experiments:
        n = exp['N']
        protocol = exp['protocol']
        if n not in protocol_data:
            protocol_data[n] = {}
        protocol_data[n][protocol] = exp
        n_values.add(n)
    
    # Find N where we have all three protocols
    common_n = []
    for n in sorted(n_values):
        if all(p in protocol_data[n] for p in ['hmvba', 'dumbomvbastar', 'finmvba']):
            common_n.append(n)
    
    table_lines = []
    table_lines.append("# Speedup of H-MVBA over Baselines\n")
    table_lines.append("| N | B | Speedup vs Dumbo-MVBA* | Speedup vs FIN-MVBA |")
    table_lines.append("|---|---|------------------------|---------------------|")
    
    for n in common_n:
        # Get B values that exist for all protocols
        b_values = set()
        for protocol in ['hmvba', 'dumbomvbastar', 'finmvba']:
            # Actually need to group by B too
            pass
        # This is more complex, implement simple version for B=1000
        b = 1000
        if all(b in [exp['B'] for exp in protocol_data[n].values() if exp['protocol'] == p] for p in ['hmvba', 'dumbomvbastar', 'finmvba']):
            hmvba = next(exp for exp in protocol_data[n].values() if exp['protocol'] == 'hmvba' and exp['B'] == b)
            dumbo = next(exp for exp in protocol_data[n].values() if exp['protocol'] == 'dumbomvbastar' and exp['B'] == b)
            fin = next(exp for exp in protocol_data[n].values() if exp['protocol'] == 'finmvba' and exp['B'] == b)
            
            speedup_dumbo = dumbo['latency_mean'] / hmvba['latency_mean'] if hmvba['latency_mean'] > 0 else 0
            speedup_fin = fin['latency_mean'] / hmvba['latency_mean'] if hmvba['latency_mean'] > 0 else 0
            
            table_lines.append(f"| {n} | {b} | {speedup_dumbo:.2f}x | {speedup_fin:.2f}x |")
    
    return "\n".join(table_lines)

def main():
    experiments = load_successful_experiments()
    print(f"Loaded {len(experiments)} successful experiments.")
    
    # Generate all tables
    tables = []
    
    tables.append(generate_table_similar_to_paper(experiments))
    tables.append("\n\n")
    tables.append(generate_protocol_comparison(experiments))
    tables.append("\n\n")
    tables.append(generate_scalability_table(experiments))
    tables.append("\n\n")
    
    # Try speedup table
    speedup_table = generate_speedup_table(experiments)
    if "| N | B |" in speedup_table:
        tables.append(speedup_table)
        tables.append("\n\n")
    
    # Write to file
    with open(OUTPUT_MD, 'w') as f:
        f.write("\n".join(tables))
    
    print(f"Tables written to {OUTPUT_MD}")
    
    # Also print summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Total successful experiments: {len(experiments)}")
    protocols = set(e['protocol'] for e in experiments)
    print(f"Protocols with data: {', '.join(sorted(protocols))}")
    
    n_values = set(e['N'] for e in experiments)
    print(f"Network sizes with data: {sorted(n_values)}")
    
    # Show example comparison for N=6, B=1000
    print("\n=== Example: N=6, B=1000 ===")
    for protocol in ['hmvba', 'dumbomvbastar', 'finmvba']:
        matches = [e for e in experiments if e['protocol'] == protocol and e['N'] == 6 and e['B'] == 1000]
        if matches:
            exp = matches[0]
            print(f"{protocol}: latency={exp['latency_mean']:.3f}s, throughput={exp['tps_mean']:.0f} tx/s")

if __name__ == '__main__':
    main()