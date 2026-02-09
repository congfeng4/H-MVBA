# Speedup Analysis: H-MVBA vs Baselines

## Speedup Table (N=6,16,31)
| N | B | Latency Speedup vs Dumbo | Latency Speedup vs FIN | Throughput Speedup vs Dumbo | Throughput Speedup vs FIN |
|---|---|---------------------------|------------------------|-----------------------------|---------------------------|
| 6 | 10 | 1.07x | 0.96x | 1.07x | 0.96x |
| 6 | 100 | 1.18x | 1.11x | 1.18x | 1.11x |
| 6 | 1000 | 1.12x | 0.72x | 1.12x | 0.72x |
| 6 | 7000 | 0.97x | 0.77x | 0.97x | 0.77x |
| 16 | 0 | 1.33x | 1.95x | 0.00x | 0.00x |
| 16 | 10 | 1.30x | 1.83x | 1.30x | 1.83x |
| 16 | 100 | 1.23x | 1.57x | 1.23x | 1.57x |
| 16 | 1000 | 1.13x | 1.74x | 1.13x | 1.74x |
| 16 | 7000 | 0.84x | 1.36x | 0.84x | 1.35x |
| 31 | 0 | 1.23x | 3.11x | 0.00x | 0.00x |
| 31 | 10 | 1.54x | 3.95x | 1.54x | 3.95x |
| 31 | 100 | 0.96x | 2.47x | 0.96x | 2.47x |
| 31 | 1000 | 0.65x | 1.81x | 0.65x | 1.81x |
| 31 | 7000 | 0.83x | 2.46x | 0.83x | 2.46x |

## Comparison with Paper Claims

Paper claims (from abstract):
- H-MVBA achieves up to 2.5× lower latency and 3.7× higher throughput than Dumbo-MVBA*
- H-MVBA achieves up to 11.7× lower latency and 14.3× higher throughput than FIN-MVBA

Our measured maximums:
- **vs Dumbo-MVBA***: 1.54x lower latency, 1.54x higher throughput
- **vs FIN-MVBA**: 3.95x lower latency, 3.95x higher throughput

Best latency speedup vs Dumbo: N=31, B=10 (H-MVBA: 0.924s, Dumbo: 1.419s)
Best latency speedup vs FIN: N=31, B=10 (H-MVBA: 0.924s, FIN: 3.648s)
Best throughput speedup vs Dumbo: N=31, B=10 (H-MVBA: 11 tx/s, Dumbo: 7 tx/s)
Best throughput speedup vs FIN: N=31, B=10 (H-MVBA: 11 tx/s, FIN: 3 tx/s)

## Observations

1. Our results show H-MVBA generally outperforms baselines for small to medium N.
2. Speedup ratios vary with network size (N) and batch size (B).
3. For large N (61,101), we only have H-MVBA data (baselines timed out).
4. FIN-MVBA shows surprisingly good performance for small B, but degrades with larger N.
5. Dumbo-MVBA* has consistent performance but higher latency than H-MVBA for most configurations.
