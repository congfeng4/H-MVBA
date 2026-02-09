#!/usr/bin/env python3
"""
Analyze results: compute speedups, generate plot data, compare with paper claims.
"""

import csv
import math
from pathlib import Path

INPUT_CSV = "aggregated_results.csv"
PLOT_LATENCY_B = "plot_latency_vs_b.csv"
PLOT_THROUGHPUT_N = "plot_throughput_vs_n.csv"
SPEEDUP_FILE = "speedup_analysis.md"

def load_successful_experiments():
    """Load successful experiments from CSV."""
    experiments = []
    with open(INPUT_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
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

def generate_latency_vs_b_data(experiments):
    """Generate CSV data for latency vs batch size B for each protocol and N."""
    # Filter for N in [6,16,31] where we have all protocols
    filtered = [e for e in experiments if e['N'] in [6,16,31]]
    
    # Group by protocol, N, B
    data = {}
    for exp in filtered:
        key = (exp['protocol'], exp['N'])
        if key not in data:
            data[key] = []
        data[key].append((exp['B'], exp['latency_mean'], exp['latency_std']))
    
    # Write CSV
    with open(PLOT_LATENCY_B, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['protocol', 'N', 'B', 'latency_mean', 'latency_std'])
        for (protocol, N), points in data.items():
            for B, latency_mean, latency_std in sorted(points, key=lambda x: x[0]):
                writer.writerow([protocol, N, B, latency_mean, latency_std])
    
    print(f"Latency vs B data written to {PLOT_LATENCY_B}")

def generate_throughput_vs_n_data(experiments):
    """Generate CSV data for throughput vs network size N for each protocol at B=1000."""
    # Filter for B=1000
    filtered = [e for e in experiments if e['B'] == 1000]
    
    # Write CSV
    with open(PLOT_THROUGHPUT_N, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['protocol', 'N', 'f', 'tps_mean', 'tps_std'])
        for exp in sorted(filtered, key=lambda x: (x['protocol'], x['N'])):
            writer.writerow([exp['protocol'], exp['N'], exp['f'], exp['tps_mean'], exp['tps_std']])
    
    print(f"Throughput vs N data written to {PLOT_THROUGHPUT_N}")

def compute_speedups(experiments):
    """Compute speedup of H-MVBA over baselines."""
    # Group by (N, B)
    groups = {}
    for exp in experiments:
        key = (exp['N'], exp['B'])
        if key not in groups:
            groups[key] = {}
        groups[key][exp['protocol']] = exp
    
    # Find keys where all three protocols exist
    speedup_results = []
    for (N, B) in sorted(groups.keys()):
        group = groups[(N, B)]
        if 'hmvba' in group and 'dumbomvbastar' in group and 'finmvba' in group:
            hmvba = group['hmvba']
            dumbo = group['dumbomvbastar']
            fin = group['finmvba']
            
            # Speedup = baseline latency / hmvba latency (higher is better for hmvba)
            latency_speedup_dumbo = dumbo['latency_mean'] / hmvba['latency_mean'] if hmvba['latency_mean'] > 0 else 0
            latency_speedup_fin = fin['latency_mean'] / hmvba['latency_mean'] if hmvba['latency_mean'] > 0 else 0
            
            # Throughput speedup = hmvba tps / baseline tps
            throughput_speedup_dumbo = hmvba['tps_mean'] / dumbo['tps_mean'] if dumbo['tps_mean'] > 0 else 0
            throughput_speedup_fin = hmvba['tps_mean'] / fin['tps_mean'] if fin['tps_mean'] > 0 else 0
            
            speedup_results.append({
                'N': N,
                'B': B,
                'latency_speedup_dumbo': latency_speedup_dumbo,
                'latency_speedup_fin': latency_speedup_fin,
                'throughput_speedup_dumbo': throughput_speedup_dumbo,
                'throughput_speedup_fin': throughput_speedup_fin,
                'hmvba_latency': hmvba['latency_mean'],
                'dumbo_latency': dumbo['latency_mean'],
                'fin_latency': fin['latency_mean'],
                'hmvba_tps': hmvba['tps_mean'],
                'dumbo_tps': dumbo['tps_mean'],
                'fin_tps': fin['tps_mean'],
            })
    
    return speedup_results

def compare_with_paper_claims(speedup_results):
    """Compare our speedups with paper claims."""
    paper_claims = {
        'dumbo': {'max_latency_speedup': 2.5, 'max_throughput_speedup': 3.7},
        'fin': {'max_latency_speedup': 11.7, 'max_throughput_speedup': 14.3},
    }
    
    # Find maximum speedups in our data
    max_latency_dumbo = max((r['latency_speedup_dumbo'] for r in speedup_results), default=0)
    max_latency_fin = max((r['latency_speedup_fin'] for r in speedup_results), default=0)
    max_throughput_dumbo = max((r['throughput_speedup_dumbo'] for r in speedup_results), default=0)
    max_throughput_fin = max((r['throughput_speedup_fin'] for r in speedup_results), default=0)
    
    # Find configurations achieving max speedups
    best_latency_dumbo = next((r for r in speedup_results if r['latency_speedup_dumbo'] == max_latency_dumbo), None)
    best_latency_fin = next((r for r in speedup_results if r['latency_speedup_fin'] == max_latency_fin), None)
    best_throughput_dumbo = next((r for r in speedup_results if r['throughput_speedup_dumbo'] == max_throughput_dumbo), None)
    best_throughput_fin = next((r for r in speedup_results if r['throughput_speedup_fin'] == max_throughput_fin), None)
    
    return {
        'max_latency_dumbo': max_latency_dumbo,
        'max_latency_fin': max_latency_fin,
        'max_throughput_dumbo': max_throughput_dumbo,
        'max_throughput_fin': max_throughput_fin,
        'best_latency_dumbo': best_latency_dumbo,
        'best_latency_fin': best_latency_fin,
        'best_throughput_dumbo': best_throughput_dumbo,
        'best_throughput_fin': best_throughput_fin,
        'paper_claims': paper_claims,
    }

def generate_speedup_report(speedup_results, comparison):
    """Generate markdown report of speedup analysis."""
    with open(SPEEDUP_FILE, 'w') as f:
        f.write("# Speedup Analysis: H-MVBA vs Baselines\n\n")
        
        f.write("## Speedup Table (N=6,16,31)\n")
        f.write("| N | B | Latency Speedup vs Dumbo | Latency Speedup vs FIN | Throughput Speedup vs Dumbo | Throughput Speedup vs FIN |\n")
        f.write("|---|---|---------------------------|------------------------|-----------------------------|---------------------------|\n")
        
        for result in speedup_results:
            f.write(f"| {result['N']} | {result['B']} | {result['latency_speedup_dumbo']:.2f}x | {result['latency_speedup_fin']:.2f}x | {result['throughput_speedup_dumbo']:.2f}x | {result['throughput_speedup_fin']:.2f}x |\n")
        
        f.write("\n## Comparison with Paper Claims\n\n")
        f.write("Paper claims (from abstract):\n")
        f.write("- H-MVBA achieves up to 2.5× lower latency and 3.7× higher throughput than Dumbo-MVBA*\n")
        f.write("- H-MVBA achieves up to 11.7× lower latency and 14.3× higher throughput than FIN-MVBA\n\n")
        
        f.write("Our measured maximums:\n")
        f.write(f"- **vs Dumbo-MVBA***: {comparison['max_latency_dumbo']:.2f}x lower latency, {comparison['max_throughput_dumbo']:.2f}x higher throughput\n")
        f.write(f"- **vs FIN-MVBA**: {comparison['max_latency_fin']:.2f}x lower latency, {comparison['max_throughput_fin']:.2f}x higher throughput\n\n")
        
        if comparison['best_latency_dumbo']:
            f.write(f"Best latency speedup vs Dumbo: N={comparison['best_latency_dumbo']['N']}, B={comparison['best_latency_dumbo']['B']} (H-MVBA: {comparison['best_latency_dumbo']['hmvba_latency']:.3f}s, Dumbo: {comparison['best_latency_dumbo']['dumbo_latency']:.3f}s)\n")
        if comparison['best_latency_fin']:
            f.write(f"Best latency speedup vs FIN: N={comparison['best_latency_fin']['N']}, B={comparison['best_latency_fin']['B']} (H-MVBA: {comparison['best_latency_fin']['hmvba_latency']:.3f}s, FIN: {comparison['best_latency_fin']['fin_latency']:.3f}s)\n")
        if comparison['best_throughput_dumbo']:
            f.write(f"Best throughput speedup vs Dumbo: N={comparison['best_throughput_dumbo']['N']}, B={comparison['best_throughput_dumbo']['B']} (H-MVBA: {comparison['best_throughput_dumbo']['hmvba_tps']:.0f} tx/s, Dumbo: {comparison['best_throughput_dumbo']['dumbo_tps']:.0f} tx/s)\n")
        if comparison['best_throughput_fin']:
            f.write(f"Best throughput speedup vs FIN: N={comparison['best_throughput_fin']['N']}, B={comparison['best_throughput_fin']['B']} (H-MVBA: {comparison['best_throughput_fin']['hmvba_tps']:.0f} tx/s, FIN: {comparison['best_throughput_fin']['fin_tps']:.0f} tx/s)\n")
        
        f.write("\n## Observations\n\n")
        f.write("1. Our results show H-MVBA generally outperforms baselines for small to medium N.\n")
        f.write("2. Speedup ratios vary with network size (N) and batch size (B).\n")
        f.write("3. For large N (61,101), we only have H-MVBA data (baselines timed out).\n")
        f.write("4. FIN-MVBA shows surprisingly good performance for small B, but degrades with larger N.\n")
        f.write("5. Dumbo-MVBA* has consistent performance but higher latency than H-MVBA for most configurations.\n")
    
    print(f"Speedup analysis written to {SPEEDUP_FILE}")

def main():
    experiments = load_successful_experiments()
    print(f"Loaded {len(experiments)} successful experiments.")
    
    # Generate plot data
    generate_latency_vs_b_data(experiments)
    generate_throughput_vs_n_data(experiments)
    
    # Compute speedups
    speedup_results = compute_speedups(experiments)
    print(f"Computed speedups for {len(speedup_results)} configurations (all three protocols).")
    
    # Compare with paper claims
    comparison = compare_with_paper_claims(speedup_results)
    
    # Generate report
    generate_speedup_report(speedup_results, comparison)
    
    # Print summary
    print("\n=== Speedup Summary ===")
    for result in speedup_results:
        print(f"N={result['N']}, B={result['B']}: "
              f"Latency: {result['latency_speedup_dumbo']:.2f}x vs Dumbo, {result['latency_speedup_fin']:.2f}x vs FIN | "
              f"Throughput: {result['throughput_speedup_dumbo']:.2f}x vs Dumbo, {result['throughput_speedup_fin']:.2f}x vs FIN")
    
    print("\n=== Max Speedups ===")
    print(f"vs Dumbo-MVBA*: {comparison['max_latency_dumbo']:.2f}x lower latency, {comparison['max_throughput_dumbo']:.2f}x higher throughput")
    print(f"vs FIN-MVBA: {comparison['max_latency_fin']:.2f}x lower latency, {comparison['max_throughput_fin']:.2f}x higher throughput")
    
    print("\n=== Paper Claims ===")
    print("Paper: up to 2.5x lower latency, 3.7x higher throughput vs Dumbo-MVBA*")
    print("Paper: up to 11.7x lower latency, 14.3x higher throughput vs FIN-MVBA")

if __name__ == '__main__':
    main()