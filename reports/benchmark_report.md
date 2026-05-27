# Benchmark report

- Input bytes: 382949
- Input size GB: 0.000383
- File read time s: 0.000652
- File read throughput GB/s: 0.587255

## CPU/GPU comparison

| Technology | Mode | Time s | Throughput GB/s | Tokens |
|---|---:|---:|---:|---:|
| CPU OpenMP-like | 2 workers | 0.004883 | 0.078420 | 29145 |
| GPU CUDA | cpu-fallback | 0.017682 | 0.021658 | 29145 |

## Top words

| Word | Count |
|---|---:|
| 18 | 2045 |
| 2015-10-18 | 2000 |
| MSRA-SA-41 | 1763 |
| 9000 | 1324 |
| INFO | 1040 |

## I/O bottleneck conclusion

I/O nie dominuje w tym pomiarze; wiekszy koszt jest po stronie obliczen.
