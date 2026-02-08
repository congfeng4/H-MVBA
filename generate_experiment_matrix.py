#!/usr/bin/env python3
"""
Generate experiment matrix for paper reproduction.
Output CSV and Markdown table.
"""

import csv

# Parameters from paper
protocols = ['hmvba', 'dumbomvbastar', 'finmvba']
N_values = [6, 16, 31, 61, 101, 201]
B_values = [0, 10, 100, 1000, 7000]
K = 10  # repetitions
C = 0   # warm-up

def compute_f(N, protocol):
    """Compute maximum f for given protocol."""
    if protocol == 'hmvba':
        # f < n/5 (20% corruption)
        return (N - 1) // 5
    else:
        # f < n/3 (33% corruption)
        return (N - 1) // 3

# Generate CSV
csv_filename = 'experiment_matrix.csv'
with open(csv_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['protocol', 'N', 'f', 'B', 'K', 'C', 'input_bytes'])
    for protocol in protocols:
        for N in N_values:
            f = compute_f(N, protocol)
            if f < 1:
                continue
            for B in B_values:
                input_bytes = 250 * B
                writer.writerow([protocol, N, f, B, K, C, input_bytes])

print(f"Generated {csv_filename}")

# Generate Markdown table
md_filename = 'experiment_matrix.md'
with open(md_filename, 'w') as mdfile:
    mdfile.write("# Experiment Matrix\n\n")
    mdfile.write("| Protocol | N | f | B | K | C | Input (bytes) |\n")
    mdfile.write("|----------|---|----|---|----|---|---------------|\n")
    for protocol in protocols:
        for N in N_values:
            f = compute_f(N, protocol)
            if f < 1:
                continue
            for B in B_values:
                input_bytes = 250 * B
                mdfile.write(f"| {protocol} | {N} | {f} | {B} | {K} | {C} | {input_bytes} |\n")

print(f"Generated {md_filename}")

# Print summary
print("\nSummary:")
print(f"Protocols: {len(protocols)}")
print(f"N values: {len(N_values)}")
print(f"B values: {len(B_values)}")
total = len(protocols) * len(N_values) * len(B_values)
print(f"Total experiments: {total}")
print(f"Total MVBA instances (K={K}): {total * K}")