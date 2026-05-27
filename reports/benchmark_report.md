# Benchmark report

- Input bytes: 15562516
- Input size GB: 0.015563
- File read time s: 0.022908
- File read throughput GB/s: 0.679346

## CPU/GPU comparison

| Technology | Mode | Time s | Throughput GB/s | Tokens |
|---|---:|---:|---:|---:|
| CPU OpenMP-like | 4 workers | 0.170246 | 0.091412 | 1649983 |
| GPU CUDA | cuda | 0.231264 | 0.067293 | 1649983 |

## Top words

| Word | Count |
|---|---:|
| 000 | 200000 |
| MAIN | 200000 |
| INFO | 173322 |
| ERROR | 73814 |
| MRAPPMASTER | 33527 |
| SPECULATOR | 33515 |
| TASK | 33473 |
| WARNING | 33466 |
| CONTAINERALLOCATOR | 33455 |
| CONTAINER | 33437 |
| TASKDISPATCHER | 33269 |
| SUCCESSFUL | 33260 |
| ASYNCDISPATCHER | 33191 |
| JOBHISTORYUTILS | 33043 |
| WARN | 30092 |
| FATAL | 22285 |
| EXECUTION | 16812 |
| STARTED | 16812 |
| REGISTERING | 16794 |
| DISPATCHER | 16794 |

## I/O bottleneck conclusion

I/O nie dominuje w tym pomiarze; wiekszy koszt jest po stronie obliczen.
