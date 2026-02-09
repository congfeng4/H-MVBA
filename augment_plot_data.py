#!/usr/bin/env python3
"""
Augment plot CSV files with missing data from aggregated_results.csv.
Adds H-MVBA data for N=61,101 to latency CSV.
"""

import pandas as pd
import os

def main():
    aggregated = 'aggregated_results.csv'
    latency_csv = 'plot_latency_vs_b.csv'
    throughput_csv = 'plot_throughput_vs_n.csv'
    
    if not os.path.exists(aggregated):
        print(f"Error: {aggregated} not found")
        return
    
    df = pd.read_csv(aggregated)
    # Only successful experiments
    df = df[df['success'] == True]
    
    # 1. Augment latency CSV
    if os.path.exists(latency_csv):
        lat_df = pd.read_csv(latency_csv)
        print(f"Original latency CSV shape: {lat_df.shape}")
    else:
        lat_df = pd.DataFrame(columns=['protocol','N','B','latency_mean','latency_std'])
    
    # Add missing H-MVBA rows for N=61,101
    hmvba_missing = df[(df['protocol'] == 'hmvba') & (df['N'].isin([61,101]))]
    if not hmvba_missing.empty:
        new_rows = []
        for _, row in hmvba_missing.iterrows():
            # Check if combination already exists
            existing = lat_df[(lat_df['protocol'] == row['protocol']) & 
                              (lat_df['N'] == row['N']) & 
                              (lat_df['B'] == row['B'])]
            if existing.empty:
                new_rows.append({
                    'protocol': row['protocol'],
                    'N': row['N'],
                    'B': row['B'],
                    'latency_mean': row['latency_mean'],
                    'latency_std': row['latency_std']
                })
        
        if new_rows:
            new_df = pd.DataFrame(new_rows)
            lat_df = pd.concat([lat_df, new_df], ignore_index=True)
            lat_df = lat_df.sort_values(['protocol','N','B'])
            lat_df.to_csv(latency_csv, index=False)
            print(f"Added {len(new_rows)} rows to {latency_csv}")
            print(f"New shape: {lat_df.shape}")
        else:
            print("No new latency rows to add")
    else:
        print("No H-MVBA data for N=61,101")
    
    # 2. Ensure throughput CSV includes all successful experiments for B=1000?
    # Actually throughput CSV appears to be aggregated across B? Need to verify.
    # We'll create a separate CSV for latency vs N for B=1000
    b_val = 1000
    df_b1000 = df[df['B'] == b_val].copy()
    if not df_b1000.empty:
        # Select relevant columns
        latency_vs_n = df_b1000[['protocol','N','f','latency_mean','latency_std']].copy()
        # Add tps columns
        latency_vs_n['tps_mean'] = df_b1000['tps_mean']
        latency_vs_n['tps_std'] = df_b1000['tps_std']
        latency_vs_n = latency_vs_n.sort_values(['protocol','N'])
        latency_vs_n.to_csv(f'latency_vs_n_B{b_val}.csv', index=False)
        print(f"Created latency_vs_n_B{b_val}.csv with shape {latency_vs_n.shape}")
    
    # 3. Create a complete latency vs B CSV for all protocols and N
    # This will be used for future plots
    complete_latency = df[['protocol','N','B','latency_mean','latency_std']].copy()
    complete_latency = complete_latency.sort_values(['protocol','N','B'])
    complete_latency.to_csv('complete_latency_vs_b.csv', index=False)
    print(f"Created complete_latency_vs_b.csv with shape {complete_latency.shape}")
    
    # 4. Create a complete throughput vs N CSV for B=1000 (or all B?)
    # We'll create for B=1000 as in paper
    df_b1000 = df[df['B'] == 1000].copy()
    if not df_b1000.empty:
        throughput_vs_n = df_b1000[['protocol','N','f','tps_mean','tps_std']].copy()
        throughput_vs_n = throughput_vs_n.sort_values(['protocol','N'])
        throughput_vs_n.to_csv('complete_throughput_vs_n_B1000.csv', index=False)
        print(f"Created complete_throughput_vs_n_B1000.csv with shape {throughput_vs_n.shape}")
    
    print("\nAugmentation complete.")

if __name__ == '__main__':
    main()